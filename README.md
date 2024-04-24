# You can monitor social networks with LLMs ?
The objective of this project is to validate a simple idea: what happens when LLM agents are used to read and summarize streaming text from social network interactions. To illustrate this concept, this repository implements an app that uses Bert, Ollama,Gemma:2b and Llama3:7b to summarize information that is available weekly in a social graph composed of Brazilian Youtube channels that cover soccer news.

## Tech Stack
In order to implement the system, the following tools are used:
  * Ollama      
    - to support local open source LLMs
  * Gemma:2b    
    - the choosen LLM to empower the streaming agents 
    - This model is in the same time powerful and cheap to run. Because the system requires one prompt to each meaningful paragraph in each video, this efficiency comes handy
* Llama3:7b
    - the choosen LLM to give the final answer
    - One bigger model was needed to enhance the user response, llama3 was the choosen one
* Youtube API
* Python as the main programming language

## The Architecture
For now, the system is executed in four consecutive steps.
1) The Youtube Transcriptions are download in to a json file
2) Each video is processed
    1) The processing first identify the meaningful chunks in each video
    2) The processed video is store in yet another json file
3) The Streaming Agents read through the processed videos, generating the abstract summary of the content
4) The final User-Response Agent takes the abstract summaries and creates a description of what happened in that week 

## Contributions and Support
If you come across any issues, bugs, or have any suggestions for improvement, please feel free to report them in the project repository. You can also contribute through pull requests.

Author: Igor Joaquim da Silva Costa
