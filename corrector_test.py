from base_corrector import correct

def ocr_correct(text_list,prob_list):
    ocr_res_corrected = correct(text_list, prob_list)
    result = ''
    for ocr in ocr_res_corrected:
        result = result + ocr + "\n"
    return result

def bbox_correct(text,prob):
    text_results = []
    text_results.append(text)
    prob_result = []
    prob_result.append(prob)
    text_results = correct(text_results, prob_result)
    # print(text_results)
    text = ''.join(text_results)
    return text