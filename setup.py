from setuptools import setup, find_packages

setup(
    name="fss-pension-mcp",
    version="1.0.0",
    description="FSS Pension MCP Server & AI Web Service",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "jinja2==3.1.2",
        "httpx==0.27.0",
        "pandas>=2.1.4",
        "numpy>=1.24.3",
        "pydantic>=2.8.0",
        "typing-extensions>=4.8.0",
        "python-dateutil>=2.8.2",
        "xmltodict>=0.13.0",
        "openai==1.12.0",
        "gunicorn==21.2.0",
        "python-dotenv==1.0.0"
    ],
    entry_points={
        'console_scripts': [
            'fss-web=fss_pension_web.simple_app:main',
        ],
    },
)