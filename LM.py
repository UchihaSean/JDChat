import Data
import numpy as np
import heapq
import random

def LM_similarity(query, document, doc_len):
    """
    Calculate similarity score for query and document based on LM with Lamplace
    """
    score = 0.0

    # Document dictionary
    doc_dict = {}
    for word in document:
        if word not in doc_dict:
            doc_dict[word] = 1
        else:
            doc_dict[word] += 1

    # Language model
    for word in query:
        if word in doc_dict:
            score += np.log(1 + (doc_dict[word] + 0.0) / doc_len)
    return score

def generate_word_sentence_dict(sentences):
    """
    Build word --> sentence id dictionary
    """
    word_sentence_dict = {}
    for i in range(len(sentences)):
        for j in range(len(sentences[i])):
            if sentences[i][j] in word_sentence_dict:
                word_sentence_dict[sentences[i][j]].add(i)
            else:
                word_sentence_dict[sentences[i][j]] = {i}
    return word_sentence_dict


def main():
    # Read Preprocessed Data
    quetions, pred_questions, answers, pred_answers = Data.read_pred_data("Data/pred_QA-pair.csv")

    pair = list(zip(quetions, pred_questions, answers, pred_answers))
    random.shuffle(pair)
    quetions, pred_questions, answers, pred_answers = zip(*pair)

    # Split Data
    split_ratio = 0.7
    split_len = int(len(quetions) * split_ratio)
    train_questions = quetions[:split_len]
    train_pred_questions = pred_questions[:split_len]
    train_answers = answers[:split_len]
    train_pred_answers = pred_answers[:split_len]
    test_questions = quetions[split_len:]
    test_pred_questions = pred_questions[split_len:]
    test_answers = answers[split_len:]
    test_pred_answers = pred_answers[split_len:]

    # Build word --> sentence dictionary
    word_sentence_dict = generate_word_sentence_dict(train_pred_questions)

    # Choose the Top K similar ones
    top_k = 5
    output = open("Data/LM.txt", 'w')
    for i in range(len(test_pred_questions)):
        top = []

        # Generate sentence id set which include at least one same word
        sentence_id_set = set()
        for j in range(len(test_pred_questions[i])):
            if test_pred_questions[i][j] in word_sentence_dict:
                sentence_id_set.update(word_sentence_dict[test_pred_questions[i][j]])

        # Generate LM similarity Score
        for j in sentence_id_set:
            score = LM_similarity(test_pred_questions[i],train_pred_questions[j], len(train_pred_questions[j]))
            heapq.heappush(top, (-score, str(j)))

        output.write("Question: " + test_questions[i].encode("utf-8") + "\n")
        output.write("Ground Truth: " + test_answers[i].encode("utf-8") + "\n")

        # Generate Top K
        for j in range(min(top_k, len(top))):
            item = int(heapq.heappop(top)[1])
            output.write("Our similar " + str(j + 1) + ": " + train_questions[item].encode("utf-8") + "\n")
            output.write("Our reply " + str(j + 1) + ": " + train_answers[item].encode("utf-8") + "\n")
        output.write("\n")

    output.close()





if __name__=="__main__":
    main()