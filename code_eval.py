from aminer_env import aminer_soay
# import black

aminer_api = aminer_soay()

# def auto_indent(code):
#     indentation = 0
#     indented_code = []
#     for line in code.split('\n'):
#         trimmed = line.strip()
#         if trimmed.startswith(('elif ', 'else:', 'except ', 'finally:')):
#             indentation -= 1
#         indented_code.append('    ' * indentation + trimmed)
#         if trimmed.endswith(':') and not trimmed.startswith('#'):
#             indentation += 1
#     return '\n'.join(indented_code)

global searchPerson 
global searchPublication
global getCoauthors 
global getPersonInterest
global getPersonPubs
global getPersonBasicInfo
global getPublication
searchPerson = aminer_api.searchPersonComp
searchPublication = aminer_api.searchPublication
getCoauthors = aminer_api.getCoauthors
getPersonInterest = aminer_api.getPersonInterest
getPersonPubs = aminer_api.getPersonPubs
getPersonBasicInfo = aminer_api.getPersonBasicInfo
getPublication = aminer_api.getPublication

process = "info = {'name': '于济凡', 'organization': '清华大学'}\nname = info['name']\norganization = info['organization']\n\nperson_list = searchPerson(name = name, organization = organization)\ntarget_person_info = person_list[0]\ntarget_person_id = target_person_info['person_id']\npublications_list = getPersonPubs(person_id = target_person_id)\n# The list was sorted by citation\nmax_citation = publications_list[0]\nfinal_result = max_citation['title']"

# intented_process = black.format_str(process, mode=black.FileMode())
# print(intented_process)

exec(process, globals())
result = final_result

print(result)