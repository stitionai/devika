# Ollama Installation Guide

This guide will help you set up Ollama for Devika. Ollama is a tool that allows you to run open-source large language models (LLMs) locally on your machine. It supports varity of models like Llama-2, mistral, code-llama and many more.

## Installation

1. go to the [Ollama](https://ollama.com) website.
2. Download the latest version of the Ollama.
3. After installing the Ollama, you have to download the model you want to use. [Models](https://ollama.com/library)
4. select the model you want to download and copy the command. for example, `ollama run llama2`.it will download the model and start the server. 
5. `ollama list` will show the list of models you have downloaded.
6. if the server isn't running then you can manually start by `ollama serve`. default address for the server is `http://localhost:11434`
7. for changing port and other configurations, follow the FAQ [here](https://github.com/ollama/ollama/blob/main/docs/faq.md)
8. for more information, `ollama [command] --help` will show the help menu. for example, `ollama run --help` will show the help menu for the run command.


## Devika Configuration

- if you serve the Ollama on a different address, you can change the port in the `config.toml` file or you can change it via UI.
- if you are using the default address, devika will automatically detect the server and and fetch the models list.
