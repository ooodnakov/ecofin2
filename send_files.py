from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import json
import wr


gauth = GoogleAuth()
drive = GoogleDrive(gauth)


def find_file(filename):
    if filename == 'results.json':
        id = '1hQMfNnhAhyL7jEFOYwQCJo5aiBGAyVuo'
    elif filename == 'feedback.json':
        id = '1wfstlhOivcoWaZR0U0tJmW3EBABmUC_5'
    else:
        id = '1NA4a-D6jXaRAGrNZaE5j9lkr6lvjVS1w'
    return drive.CreateFile({'id': id})


def read_results():
    file_res = find_file('results.json')
    return json.loads(file_res.GetContentString())


def write_results(results):
    file_res = find_file('results.json')
    file_res.SetContentString(json.dumps(results, indent=4, sort_keys=True))
    file_res.Upload()


def clear(id):
    results = read_results()
    results.pop(id)
    write_results(results)


def read_problems():
    file_problems = find_file('problems1.json')
    return json.loads(file_problems.GetContentString())


def read_feedback():
    file_feedback = find_file('feedback.json')
    return json.loads(file_feedback.GetContentString())


def write_feedback(feedback):
    file_feedback = find_file('feedback.json')
    file_feedback.SetContentString(
        json.dumps(
            feedback,
            indent=4,
            sort_keys=True,
            ensure_ascii=False))
    file_feedback.Upload()


# f_pr = find_file('problems1.json')
# f_pr.SetContentString(
#     json.dumps(
#         wr.read_problems(),
#         indent=4,
#         ensure_ascii=False
#     )
# )
# f_pr.Upload()

# file_list = drive.ListFile(
# {'q': "'root' in parents and trashed=false"}).GetList()
# for file1 in file_list:
#     print(file1['title'], file1['id'])


write_results(wr.read_results())
write_feedback(wr.read_feedback())
