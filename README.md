# You can monitor social networks with LLMs ?
The objective of this project is to validate a simple idea: what happens when LLM agents are used to read and summarize streaming text from social network interactions. To illustrate this concept, this repository implements a bot to summarize information that is available weekly in a social graph composed of Youtube channels that cover soccer news.

## Tech Stack
In order to implement the system, the following tools are used:
  * Gemini-1.5-flash 
    - the choosen LLM to empower the streaming agents 
    - This model is in the same time powerful and cheap to run. Because the system requires one prompt to each meaningful paragraph in each video, this efficiency comes handy
  * Youtube DATA API
  * Python 3.12 

## The Architecture
For now, the system is executed in four consecutive steps.
1) Youtube Transcriptions (and comments?) are scrapped from the web 
2) Each video is processed
    1) Some N agents do extractive summarization on the transcriptions
    2) Some M agents to abstractive summarization on the previous summarization (typically, M<<N)
3) The final User-Response Agent takes the abstract summaries and creates a description of what happened in that week 

## Contributions and Support
If you come across any issues, bugs, or have any suggestions for improvement, please feel free to report them in the project repository. You can also contribute through pull requests.

Author: Igor Joaquim da Silva Costa
