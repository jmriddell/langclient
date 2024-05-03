# langclient

Simple interactive console language client for OpenAI API language models.

> [!IMPORTANT]
> API Key not included

## Features
* Easy language model selection
* Read local files (Check [Token limitations](https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo) for large files)

## Installation

### Prerequisites

* git
* python >= 3.11

For termux you will also need to install:

* rust
* binutils


### Install

```bash
pip install git+https://github.com/jmriddell/langclient.git#main
```

## Usage

### Run 

```bash
langclient [--api-key-file <api-key-file> | --api-key <api-key>]
```
Api key file should contain a single line with the api key.

If api key not provided in any way, the program will prompt for it.

### Model Selection
At startup select the model to interact.

```bash
[?] Select a model:
 > gpt-3.5-turbo-0125
   gpt-4-turbo-2024-04-09
   gpt-4
   gpt-4-32k
```

Check the [pricing cuotas](https://openai.com/pricing) and [usage dashboard](https://platform.openai.com/usage).

### Local file input
Files can be included in the sending message to the api using angle brackts.

```yaml
You:
Write a short description of the <readme.md> file

Assistant:
The readme.md file provides a brief overview of the langclient, a simple interactive console language client for OpenAI API language models. It includes information on installation prerequisites and instructions, as well as guidance on usage, model selection, and inputting local files. The file also emphasizes the importance of not including the API key. Links to relevant documentation and resources are also provided.
```

Works with subdirectories and names with spaces like `<subfolder/name with spaces.txt>`.
