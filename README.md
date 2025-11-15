# Chroma TUI

A terminal user interface (TUI) for browsing and managing ChromaDB instances.

## Features

- Browse collections and view document counts
- View complete documents with metadata and embeddings
- Create and delete collections
- Add documents to collections
- Search documents using semantic similarity
- Interactive and intuitive interface

## Installation

### From PyPI

```bash
pip install chroma-tui
```

### From Source

1. Clone this repository:
   ```bash
   git clone https://github.com/Mukhunyeledzi-Muthuphei/chromadb-tui.git
   cd chromadb-tui
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

## Usage

Run the TUI from your terminal:

```bash
chroma-tui
```

You'll be prompted to enter your ChromaDB server connection details (host and port). Once connected, you can:

- **View Collections**: Browse all collections and their document counts
- **Create Collection**: Add new collections to your database
- **Delete Collection**: Remove collections from your database
- **View Document**: Display complete document details including text, metadata, and optional embedding vectors
- **Search Documents**: Perform semantic similarity searches across documents
- **Add Document**: Insert new documents into collections

## Requirements

- Python 3.8+
- ChromaDB server instance (running separately)

## License

MIT License
