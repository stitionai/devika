# Search Engine Setup for Devika

Devika supports three search engines: **Bing**, **Google**, and **DuckDuckGo**. While **DuckDuckGo** does not require any API keys, **Bing** and **Google** do. Follow the steps below to set up the API keys for Bing and Google.

## 1. Bing Search API Setup

### Step 1: Create an Azure Account
- Visit the [Azure website](https://azure.microsoft.com/en-us/free/) and create a free account.

### Step 2: Access the Bing Search API
- Go to the [Bing Search API](https://www.microsoft.com/en-us/bing/apis/bing-web-search-api) page.
- Click on the `Try now` button.
- Sign in or sign up using your Azure account.

### Step 3: Create a Resource Group
- If you don't have a resource group, create one during the setup process.

### Step 4: Create a Bing Search API Resource
- Fill in the necessary details for your Bing Search API resource.
- Click on the `Review and create` button.
- If everything is correct, click on the `Create` button.

### Step 5: Retrieve Your API Keys and Endpoint
- Once the resource is created, go to the `Keys and Endpoint` tab.
- ![Keys and Endpoint](images/bing-1.png)
- Copy either `Key1` or `Key2`.
- Paste the key into the `API_KEYS` field with the name `BING` in the `config.toml` file located in the root directory of Devika, or you can set it via the UI.
- Copy the `Endpoint` and paste it into the `API_Endpoints` field with the name `BING` in the `config.toml` file located in the root directory of Devika, or you can set it via the UI.

## 2. Google Search API Setup

### Step 1: Create a Google Cloud Project
- If you don't have one, create a Google Cloud Project via the [Google Cloud Console](https://console.cloud.google.com/).

### Step 2: Enable the Custom Search API
- Visit the [Google Custom Search API Documentation](https://developers.google.com/custom-search/v1/overview).
- Click on `Get a Key`.
- Select your project or create a new one.
- ![Create Project](images/google.png)
- This will enable the Custom Search API for your project and generate an API key.

### Step 3: Retrieve Your API Key
- Copy the API key.
- Paste it in the `API_KEYS` field with the name `GOOGLE_SEARCH` in the `config.toml` file located in the root directory of Devika, or you can set it via the UI.

### Step 4: Create a Custom Search Engine
- Go to the [Google Custom Search Engine](https://programmablesearchengine.google.com/controlpanel/all) website.
- Click on the `Add` button to create a new search engine.
- ![Create Search Engine](images/google-2.png)
- After creating the engine, copy the `Search Engine ID`.
- Paste it in the `API_Endpoints` field with the name `GOOGLE_SEARCH_ENGINE_ID` in the `config.toml` file located in the root directory of Devika, or you can set it via the UI.
```

