# from google import genai
# import dotenv
#
# dotenv.load_dotenv()
#
# client = genai.Client()
#
# response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents="Explain how AI works in a few words",
# )
#
# print(response.text)
import asyncio
import time

import src.treeList as treeList
import src.fileUtil as fileUtil
import json

import src.project_helper_mcpclient as project_helper_mcpclient




if __name__ == '__main__':

    # tree_string, path_dictionary= treeList.generate_tree_with_functions(r"/home/wenzhen/PycharmProjects/youtube2podcast")
    #
    # fileUtil.combine_files(path_dictionary, "out.txt")

    # search_prompt = "Can you scan this folder (/home/wenzhen/PycharmProjects/youtube2podcast), and give me the arborescence"
    search_prompt = "Can you checkout this git repo (https://github.com/duwenzhen/project_helper.git) to the local machine, then scan the folder on the local machine, then combine all the files of the path_dictionary into to one big combined file"

    functionResponse, results_txt = asyncio.run(project_helper_mcpclient.run(search_prompt))

    res_dict = json.loads(functionResponse.content[0].text)
    context_file_path = res_dict["output_file_path"]
    path_dictionary = res_dict["path_dictionary"]


    for id, path in path_dictionary.items():
        if path.endswith(".py") and not path.endswith("__init__.py"):
            prompt = f"""please create unit tests for this file {path}, with the context file {context_file_path}"""
            functionResponse, results_txt = asyncio.run(project_helper_mcpclient.run(prompt))
            print(functionResponse)
            open(path.replace(".py", "_test.py"), "w").write(functionResponse.content[0].text)
            time.sleep(60)

            prompt = f"""please add comments for this file {path}, with the context file {context_file_path}"""
            functionResponse, results_txt = asyncio.run(project_helper_mcpclient.run(prompt))
            print(functionResponse)
            open(path, "w").write(functionResponse.content[0].text)
            time.sleep(60)






