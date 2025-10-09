# fx-execution-bot

A Python-based trading bot that interacts with the Saxo Bank OpenAPI to fetch live FX spot prices, monitor account balances, manage positions, and place orders.   
This project started as a way to explore automated trading and API-based execution in FX markets. Over time, I plan to expand it into a framework that supports strategy backtesting, risk management, and automated execution. 
<br>
I built this project to gain hands-on experience with:
- Low-latency trading APIs and REST interactions
- Practical aspects of trade execution and portfolio monitoring
- Applying programming to real-world finance contexts

Using 
- rich library, beautiful live displays
pip install -r requirements.txt

Use rich + textual + typer as your CLI foundation for Core Terminal & CLI Experience
Use pandas, numpy for Data Handling & Analytics
Use aiohttp + websockets for real-time for Market Data Integration but I will add this later and use yfinance or other data to simulate the real market later. 

Use plotly or rich live charts inside a textual interface for Visualization & Monitoring, make interactive charts

Use asyncio + uvloop for Performance & Concurrency

cProfile to profile my code.

Testing/Maintaining

pytest - For testing strategies, APIs, and data pipelines.
loguru - Powerful and beautiful logging.
docker - Containerize your terminal for deployment.

