from transformers import MarianTokenizer, MarianMTModel
from tqdm import tqdm
from torch import cuda


#tr-az translater
tr_az_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-tr-az")
tr_az_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-tr-az").to("cuda")

#input data
tr_data_path = "../data/tr-en/tr-en-open-subtitles/OpenSubtitles.tr-en.tr"
tr_data_file = open(tr_data_path, "r")
en_data_path = "../data/tr-en/tr-en-open-subtitles/OpenSubtitles.tr-en.en"
en_data_file = open(en_data_path, "r")

#parameters
data_file = tr_data_file
initial_offset = 300000 #skip the first number of lines
data_out_size = 200000 #number of output lines
batch_size =  40 #size of each batch
assert data_out_size % batch_size == 0, "Batch size doesn't divide total data out cleanly"
num_of_batches = int(data_out_size/batch_size) #number of batches

print(f"\nNumber of Batches ={num_of_batches}\nBatch size ={batch_size}")

#output files
tr_file_out_path = "./back-trans-open-sub.tr"
tr_file_out = open(tr_file_out_path, "w")
az_file_out_path =  "./back-trans-open-sub.az"
az_file_out = open(az_file_out_path, "w")
en_file_out_path = "./back-trans-open-sub.en"
en_file_out = open(en_file_out_path, "w")

#offset input files
print(f"Offsetting input files to {initial_offset} lines")
for i in tqdm(range(0, initial_offset)):
  data_file.readline()
  en_data_file.readline()

#function that generates a batch, translates it, and writes the relevant output files (except english)
def batch_and_write():
  #get the input text
  src_text = [None]*batch_size
  for i in range(0,batch_size):
    src_text[i]=data_file.readline()
    if src_text[i][0]=="-": #this is a little bit of data cleaning for a common issue in open subtitles
      src_text[i]=src_text[i][2:]
  #batch
  batch = tr_az_tokenizer.prepare_seq2seq_batch(src_texts=src_text, return_tensors="pt").to('cuda')
  #generate
  gen = tr_az_model.generate(**batch).to('cuda')
  #decode
  words = tr_az_tokenizer.batch_decode(gen, skip_special_tokens=True)
  #write the output files
  for i in range(0, batch_size):
    tr_file_out.write(src_text[i])
    az_file_out.write(words[i]+"\n")
  #clear cuda cache
  del src_text
  del batch
  del gen
  del words
  cuda.empty_cache()

#run our batches
print("Translating")
for i in tqdm(range(num_of_batches)):
  batch_and_write()
  #and also write the en file
  for j in range(0, batch_size):
    line = en_data_file.readline()
    if line[0]=="-":
      line = line[2:]
    en_file_out.write(line)


