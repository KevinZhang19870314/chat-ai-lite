from datetime import datetime

from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate

from db import crud_user
from mad_hatter.decorators import tool


@tool
def get_the_time(tool_input, bot):
	"""Replies to "what time is it", "get the clock", "现在几点了？"，“几点钟了？” and similar questions. Input is always None."""

	return str(datetime.now())


@tool
def get_the_day_of_week(tool_input, bot):
	"""根据当前标准时间获取星期几或者礼拜几。 始终没有输入参数。"""
	today = datetime.today()
	weekday = today.weekday()

	# 将星期几转换为对应的字符串
	weekday_str = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
	return str(f"今天是{weekday_str[weekday]}")


# @tool
# def anything_about_the_old_driver(question, bot):
# 	"""使用这个工具谈论关于老司机这个人。 任何与老司机这个人相关的任何事情，注意：请使用中文作答。 输入是关于老司机相关的话题或者问题。"""
#
# 	human_template = f"""老司机是老鹅，他是高级工程师，他有很多粉丝，他的粉丝遍布全中国，
# 	车展上的嫩模都是他的粉丝，他是接触的思想家，哲学家。他的杰出作品微信会员卡系统很牛逼，
# 	还有最近的flink风控系统牛逼的很。。
#
# 	以上是对老司机的简单介绍，当然你可以用幽默诙谐的、无厘头的、甚至调侃的语言自由发挥来回答我的问题，下面是关于老司机的问题：
#
# 	问题: {question}
# 	使用中文回复关于老司机的任何事情如下:
# 	"""
# 	human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
#
# 	chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])
# 	sentence = bot.llm(chat_prompt.format_prompt(question=question).to_messages())
#
# 	return sentence.content


# @tool(return_direct=True)
# def get_my_user_information(tool_input, bot):
# 	"""获取当前登录的用户个人信息。 始终没有输入参数。"""
#
# 	print(f"\n==========================={bot.email}===========================\n")
# 	user = crud_user.get_user_by_email(next(bot.db()), bot.email)
# 	if not user:
# 		return "No user information"
#
# 	content = f"""您的登录用户信息如下：\n
# 头像：![头像]({user.avatar} "=60x40")\n
# 邮箱: {user.email}\n
# 描述: {user.description}\n
# 剩余使用次数: {user.total_requests - user.used_requests}\n
# 是否飞书用户：{user.is_feishu_user}
# """
# 	return content
