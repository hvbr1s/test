import os
import uuid
from flask import Flask, render_template, request, make_response, redirect, jsonify
from web3 import Web3
from llama_index import GPTSimpleVectorIndex, download_loader
from langchain.agents import initialize_agent, Tool, load_tools
from langchain.llms import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize web3
web3 = Web3(Web3.HTTPProvider("https://rpc-mumbai.maticvigil.com/"))

# Initialize LLM
llm = OpenAI(temperature=0.5)

# Prepare Zendesk tool
ZendeskReader = download_loader("ZendeskReader")
loader = ZendeskReader(zendesk_subdomain="ledger", locale="en-us")
documents = loader.load_data()

# Prepare Reddit tool
subreddits = ['ledgerwallet']
search_keys = []
post_limit = 5

RedditReader = download_loader('RedditReader')
loader = RedditReader()
documents = loader.load_data(subreddits=subreddits, search_keys=search_keys, post_limit=post_limit)
index = GPTSimpleVectorIndex.from_documents(documents)

def start_query_func(index):
    def query_func(q):
        return index.query(q)
    return query_func

reddit_index_tool = Tool(
    name="Reddit Index",
    func=lambda q: start_query_func(index),
    description=f"Useful when you want to read relevant posts and top-level comments in subreddits.",
)

# Create GPTSimpleVectorIndex with the loaded Zendesk documents
index = GPTSimpleVectorIndex.from_documents(documents)

def generate_query_func(index):
    def query_func(q):
        return index.query(q)
    return query_func

zendesk = Tool(
    name="Zendesk",
    func=generate_query_func(index),
    description=f"Useful when you want to search for relevant information from Ledger's Zendesk support articles.",
)

# Prepare toolbox
serpapi_tool = load_tools(["serpapi"])[0]
tools = [serpapi_tool, zendesk, reddit_index_tool]

# Run agent
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

# Define Flask app
app = Flask(__name__)
app = Flask(__name__, static_folder='static')


# Define authentication function
def authenticate(signature):
    w3 = Web3(Web3.HTTPProvider(os.environ['WEB3_PROVIDER']))
    address = w3.eth.accounts.recover("Access to chat bot", signature)
    balance = int(contract.functions.balanceOf(address).call())
    if balance > 0:
        token = uuid.uuid4().hex
        response = make_response(redirect('/gpt'))
        response.set_cookie("authToken", token, httponly=True, secure=True, samesite="strict")
        return response
    else:
        return "You don't have the required NFT!"


# Define function to check for authToken cookie
def has_auth_token(request):
    authToken = request.cookies.get("authToken")
    return authToken is not None

# Define Flask endpoints
@app.route("/")
def home():
    return render_template("auth.html")

@app.route("/auth")
def auth():
    signature = request.args.get("signature")
    response = authenticate(signature)
    return response

@app.route("/gpt")
def gpt():
    if has_auth_token(request):
        return render_template("index.html")
    else:
        return redirect("/")

@app.route('/api', methods=['POST'])
def react_description():
    print(request.json)
    # Get user input from request
    user_input = request.json.get('user_input')
    
    # Run the OpenAI agent on the user input
    output = agent.run(user_input)
    
    # Return the output as JSON
    return jsonify({'output': output})

# Start the Flask app
if __name__ == '__main__':
    app.run(port=8000)


ADDRESS = "0xb022C9c672592c274397557556955eE968052969"
ABI = [{"inputs":[{"internalType":"string","name":"_name","type":"string"},{"internalType":"string","name":"_symbol","type":"string"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"string","name":"tokenURI","type":"string"}],"name":"safeMint","outputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"index","type":"uint256"}],"name":"tokenByIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"index","type":"uint256"}],"name":"tokenOfOwnerByIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]
contract = web3.eth.contract(address=ADDRESS, abi=ABI)
