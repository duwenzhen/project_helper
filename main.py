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

import src.treeList as treeList
import src.fileUtil as fileUtil

if __name__ == '__main__':

    tree_string, path_dictionary= treeList.generate_tree_with_functions(r"C:\Users\Wenzhen\PyCharmProject\youtube2podcast")


    fileUtil.combine_files(path_dictionary, "out.txt")