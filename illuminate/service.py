import logging

import dotenv
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from illuminate.log_utils import setup_logging

dotenv.load_dotenv()


setup_logging()
logger = logging.getLogger('illuminate.domain')


class PerspectiveItem(BaseModel):
    pov: str = Field(description='Selected perspective')
    select_reason: str = Field(description='Reason for selecting this perspective')


class PerspectiveSelection(BaseModel):
    perspectives: list[PerspectiveItem] = Field(
        description='List of 2-3 selected perspectives with reasons',
        min_items=2,
        max_items=3,
    )
    overall_rationale: str = Field(description='Brief overall explanation of the selection')


def create_select_chain():
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

    select_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                """You are an expert at analyzing content.
Your task is to select the most relevant perspectives for summarizing the given content.
Choose 2-3 perspectives that would be most insightful for summarization.""",
            ),
            HumanMessagePromptTemplate.from_template(
                """Content: {content}

Available perspectives: {povs}

Select the most relevant perspectives and explain briefly why each is appropriate for this content.
Also provide a brief overall rationale for your selection.

For each perspective, provide:
1. The perspective name (pov)
2. The reason for selecting it (select_reason)

Return 2-3 perspectives total.""",
            ),
        ],
    )
    logger.debug('select chain을 만들었습니다.')
    return select_prompt | llm.with_structured_output(PerspectiveSelection, method='function_calling')


def create_adapt_chain():
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

    adapt_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                """You are an expert at content summarization.
Your task is to adapt the selected perspectives to the summarization task.""",
            ),
            HumanMessagePromptTemplate.from_template(
                """Content: {content}

Selected perspectives: {selected_povs}
Overall rationale: {overall_rationale}

Explain how these perspectives should be applied to create a comprehensive summary.""",
            ),
        ],
    )

    logger.debug('adapt chain을 만들었습니다.')
    return adapt_prompt | llm | StrOutputParser()


def create_summary_chain():
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

    summary_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                """You are an expert summarizer.
Create a concise but comprehensive summary of the content.""",
            ),
            HumanMessagePromptTemplate.from_template(
                """Content: {content}

Adaptation guidance: {adapted_perspectives}

Create a detailed summary that captures the essence of the content while applying the adaptation guidance.""",
            ),
        ],
    )

    return summary_prompt | llm | StrOutputParser()


def create_prettify_chain():
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

    prettify_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                """You are an expert at formatting text for Discord.
Your task is to take a summary and format it for optimal readability in Discord.

Follow these guidelines:
1. Use Markdown formatting that works well in Discord
2. Use headings with # (maximum 3 #'s)
3. Add one emoji before each heading to make it visually appealing
4. If there are tables, convert them to a more readable format since Discord doesn't render tables well
5. Make lists and bullet points clear and well-formatted
6. Preserve the original content meaning but optimize the format""",
            ),
            HumanMessagePromptTemplate.from_template(
                """Here is the summary to format for Discord:

{summary}

Please format this for optimal readability in Discord.""",
            ),
        ],
    )

    logger.debug('summary chain을 만들었습니다.')
    return prettify_prompt | llm | StrOutputParser()


def summarizer(content: str, povs: list[str]):
    select = create_select_chain()
    adapt = create_adapt_chain()
    summarize = create_summary_chain()
    prettify = create_prettify_chain()

    def prepare_select_input(content):
        logger.info('컨텐츠를 요약합니다.')
        return {
            'content': content,
            'povs': '\n- '.join(povs),
        }

    def prepare_adapt_input(selected):
        perspectives_text = '\n'.join(
            [f'- {item.pov}: {item.select_reason}' for item in selected.perspectives],
        )
        logger.debug('다음 pov들이 선택되었습니다:: %s', perspectives_text)
        return {
            'content': content,
            'selected_povs': perspectives_text,
            'overall_rationale': selected.overall_rationale,
        }

    def prepare_summary_input(adapted):
        logger.info('pov 적용을 완료했습니다.')
        return {
            'content': content,
            'adapted_perspectives': adapted,
        }

    def prepare_prettify_input(summary):
        logger.info('요약 결과를 디스코드에 맞게 수정합니다.')
        return {'summary': summary}

    chain = (
        RunnableLambda(prepare_select_input)
        | select
        | RunnableLambda(prepare_adapt_input)
        | adapt
        | RunnableLambda(prepare_summary_input)
        | summarize
        | RunnableLambda(prepare_prettify_input)
        | prettify
    )

    return chain.invoke(content)


if __name__ == '__main__':
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

    def transform_fn(content):
        return {
            'content': content,
            'povs': 'this is pov',
        }

    select_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template('You are an expert at analyzing content.'),
            HumanMessagePromptTemplate.from_template('{content} {povs}'),
        ],
    )
    chain = RunnableLambda(transform_fn) | select_prompt | llm | StrOutputParser()
    print(chain.invoke({'content': 'this is content'}))
