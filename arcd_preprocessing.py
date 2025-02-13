# coding=utf-8
#
# This script applies AraBERT's cleaning process and segmentation to ARCD or
# any SQUAD-like structured files and "naively" re-alligns the answers start positions

import tensorflow as tf
from preprocess_arabert import preprocess, never_split_tokens
from tokenization import BasicTokenizer

import json
tf = tf.compat.v1
flags = tf.flags
FLAGS = flags.FLAGS
from farasa import segmentation as farasa
## Required parameters
flags.DEFINE_string(
    "input_file", None,
    "The input json file with a SQUAD like structure.")

flags.DEFINE_string("output_file", None,
                    "The ouput json file with AraBERT preprocessing applied.")

flags.DEFINE_bool(
    "do_farasa_tokenization", None,
    "True for AraBERTv1 and False for AraBERTv0.1")

## Other parameters
flags.DEFINE_string("path_to_farasa", None,
                    "path to the FarasaSegmenterJar.jar file required when "
                    "do_farasa_tokenization is enabled")

bt = BasicTokenizer()
def clean_preprocess(text,do_farasa_tokenization,farasa):
  text = " ".join(bt._run_split_on_punc(preprocess(text,do_farasa_tokenization=do_farasa_tokenization,farasa=farasa)))
  text = " ".join(text.split())#removes extra whitespaces
  return text


def main(_):
  tf.logging.set_verbosity(tf.logging.INFO)


  


  with tf.gfile.Open(FLAGS.input_file, "r") as reader:
    input_data = json.load(reader)["data"]

  for entry in input_data:
    for paragraph in entry["paragraphs"]:
      paragraph["context"] = clean_preprocess(paragraph["context"],
                        do_farasa_tokenization=FLAGS.do_farasa_tokenization,
                        farasa=farasa)
      for qas in paragraph["qas"]:
        qas["question"]= clean_preprocess(qas["question"],
                            do_farasa_tokenization=FLAGS.do_farasa_tokenization,
                            farasa=farasa)
        qas["answers"][0]["text"] = clean_preprocess(qas["answers"][0]["text"],
                                  do_farasa_tokenization=FLAGS.do_farasa_tokenization,
                                  farasa=farasa)
        qas["answers"][0]["answer_start"] = paragraph["context"].find(qas["answers"][0]["text"])
        if qas["answers"][0]["answer_start"] == -1:
          tf.logging.warning("Could not find answer for question '%d' : '%s' vs. '%s'",
                                    qas["id"],paragraph["context"], qas["answers"][0]["text"])

  input_data = {
      'data': input_data,
      'version': "1.1",
      "preprocess": "True",
    }
  with tf.gfile.Open(FLAGS.output_file, "w") as writer:
    json.dump(input_data,writer)

if __name__ == "__main__":
  flags.mark_flag_as_required("input_file")
  flags.mark_flag_as_required("output_file")
  flags.mark_flag_as_required("do_farasa_tokenization")
  tf.app.run()
