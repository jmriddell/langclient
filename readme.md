# langclient

Simple interactive console language client for OpenAI. Useful for using GPT-4 with an API subscription.

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

```bash
langclient [--api-key-file <api-key-file> | --api-key <api-key>]
```
Api key file should contain a single line with the api key.

If api key not provided in any way, the program will prompt for it.