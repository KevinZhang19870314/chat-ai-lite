import traceback
from typing import Optional, Any

from langchain_community.llms import OpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field

MY_FAVORITES_PARSER_TEMPLATE = """
你是一个角色解析器，你需要根据用户查询问题和格式指令解析出角色字段的具体值。

需要解析出的字段如下:
limit：最大记录数，如果没有解析出来，则使用默认值。
page：当前页，如果没有解析出来，则使用默认值。
category：字符串，将会根据用户的搜索关键字判断当前属于哪个分类，如果无法判断或者解析出错，则默认为'all'。
terms：字符串列表，将会根据用户搜索关键字拆分为多个中文term，生成一个list列表保存到terms中去。

解析后需要将字段作为一个JSON返回。

{format_instructions}

# 用户查询问题为:
{query}
"""


class MyFavoriteParserParameter(BaseModel):
	limit: Optional[str] = Field(None, description="从查询返回的最大记录数，通常用于实现分页。 默认值为 15。")
	page: Optional[str] = Field(None, description="查询当前页，为了实现分页。 默认值为 1。")
	category: Optional[str] = Field(None, description="""
		记录表中的角色分类，字符串类型，值包括'all', 'likes', 'character', 'education', 'travel', 'game', 'translate', 'develop', 'tool', 'medical', 'food', 'marketing', 'other'。
		枚举值对应的中文为'全部', '喜欢', '人物', '教育', '旅行', '游戏', '翻译', '开发', '工具', '医疗', '美食', '营销', '其他'。
		如果解析此字段出错，返回'all'。
		默认为'all'。
	""")
	terms: Optional[list[str]] = Field(None, description="拆分后的搜索关键字。默认为空数组[]。")


def my_favorites_parser(user_query: str):
	parser = PydanticOutputParser(pydantic_object=MyFavoriteParserParameter)
	prompt = PromptTemplate(
		template=MY_FAVORITES_PARSER_TEMPLATE,
		input_variables=["query"],
		partial_variables={"format_instructions": parser.get_format_instructions()},
	)

	_input = prompt.format_prompt(query=user_query)
	try:
		model_name = "text-davinci-003"
		temperature = 0.0
		model = OpenAI(model_name=model_name, temperature=temperature)
		output = model(_input.to_string())
		response: MyFavoriteParserParameter = parser.parse(output)

		return response
	except Exception as e:
		traceback.print_exc()
		return None
