# src/chroma_tui/tui_rich.py

import chromadb
import json
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich import box


class ChromaTUI:
    """A simple TUI for ChromaDB using Rich."""
    
    def __init__(self):
        self.console = Console()
        self.client = None
        self.collections = []
        
    def clear_screen(self):
        """Clear the console screen."""
        self.console.clear()
        
    def show_title(self):
        """Display the application title."""
        title = Text("ChromaDB TUI", style="bold magenta")
        title.justify = "center"
        self.console.print(Panel(title, box=box.DOUBLE, style="cyan"))
        self.console.print()
        
    def get_connection_details(self):
        """Get connection details from user input."""
        self.clear_screen()
        self.show_title()
        
        self.console.print("[bold]Connection Settings[/bold]", style="blue")
        self.console.print()
        
        host = Prompt.ask("Host", default="localhost")
        port = Prompt.ask("Port", default="8000")
        
        try:
            port = int(port)
            return host, port
        except ValueError:
            self.console.print("[red]Invalid port number![/red]")
            return None, None
            
    def connect_to_chroma(self, host, port):
        """Connect to ChromaDB."""
        try:
            self.console.print(f"[yellow]Connecting to {host}:{port}...[/yellow]")
            
            # Create ChromaDB client using v2 server approach
            settings = chromadb.Settings(
                chroma_server_host=host,
                chroma_server_http_port=port,
                chroma_api_impl="chromadb.api.fastapi.FastAPI"
            )
            self.client = chromadb.Client(settings)
            
            # Test connection by trying to list collections
            collections = self.client.list_collections()
            
            self.console.print("[green]Connected successfully![/green]")
            
            # Load collections
            self.load_collections()
            
            return True
        except Exception as e:
            self.console.print(f"[red]Connection failed: {str(e)}[/red]")
            self.client = None
            return False
            
    def load_collections(self):
        """Load collections from ChromaDB."""
        if not self.client:
            return
            
        try:
            collections = self.client.list_collections()
            self.collections = []
            
            for collection in collections:
                # Get collection info
                count = collection.count()
                metadata = collection.metadata or {}
                
                self.collections.append({
                    "name": collection.name,
                    "count": count,
                    "metadata": metadata,
                    "collection": collection
                })
        except Exception as e:
            self.console.print(f"[red]Failed to load collections: {str(e)}[/red]")
            self.collections = []
            
    def show_collections(self):
        """Display collections in a table."""
        self.clear_screen()
        self.show_title()
        
        if not self.collections:
            self.console.print("[yellow]No collections found.[/yellow]")
            self.console.print()
            return
        
        table = Table(title="Collections", box=box.ROUNDED)
        table.add_column("Name", style="cyan", width=25)
        table.add_column("Documents", justify="right", style="magenta", width=12)
        table.add_column("Metadata", style="green")
        
        for collection in self.collections:
            metadata_str = json.dumps(collection["metadata"]) if collection["metadata"] else "{}"
            table.add_row(
                collection["name"], 
                str(collection["count"]), 
                metadata_str[:50] + "..." if len(metadata_str) > 50 else metadata_str
            )
            
        self.console.print(table)
        self.console.print()
        
    def show_collection_details(self, collection_name):
        """Show details for a specific collection."""
        self.clear_screen()
        self.show_title()
        
        # Find the collection
        collection_info = None
        for col in self.collections:
            if col["name"] == collection_name:
                collection_info = col
                break
                
        if not collection_info:
            self.console.print(f"[red]Collection '{collection_name}' not found.[/red]")
            return
            
        collection = collection_info["collection"]
        
        self.console.print(f"[bold]Collection: {collection_name}[/bold]", style="blue")
        self.console.print(f"Document count: {collection_info['count']}")
        self.console.print()
        
        try:
            # Get documents from the collection
            result = collection.peek(limit=10)  # Get first 10 documents
            
            if not result['ids']:
                self.console.print("[yellow]No documents in this collection.[/yellow]")
                return
                
            docs_table = Table(title="Documents (showing first 10)", box=box.ROUNDED)
            docs_table.add_column("ID", style="cyan", width=15)
            docs_table.add_column("Document", style="white", width=50)
            docs_table.add_column("Metadata", style="green", width=30)
            
            for i, doc_id in enumerate(result['ids']):
                document = result['documents'][i] if i < len(result['documents']) else ""
                metadata = result['metadatas'][i] if i < len(result['metadatas']) else {}
                
                # Truncate long content
                doc_content = str(document)[:47] + "..." if len(str(document)) > 50 else str(document)
                metadata_str = json.dumps(metadata) if metadata else "{}"
                metadata_str = metadata_str[:27] + "..." if len(metadata_str) > 30 else metadata_str
                
                docs_table.add_row(str(doc_id), doc_content, metadata_str)
                
            self.console.print(docs_table)
            self.console.print()
            
        except Exception as e:
            self.console.print(f"[red]Error loading documents: {str(e)}[/red]")
        
    def show_main_menu(self):
        """Display the main menu options."""
        menu = Panel(
            "[1] View Collections\n"
            "[2] Create Collection\n" 
            "[3] Delete Collection\n"
            "[4] View Document\n"
            "[5] Search Documents\n"
            "[6] Add Document\n"
            "[0] Exit",
            title="Main Menu",
            box=box.ROUNDED,
            style="blue"
        )
        self.console.print(menu)
        self.console.print()
        
    def main_loop(self):
        """Main application loop."""
        while True:
            # Get connection details
            host, port = self.get_connection_details()
            if host is None:
                continue
                
            # Try to connect
            if not self.connect_to_chroma(host, port):
                if not Confirm.ask("Try again?"):
                    break
                continue
                
            # Main menu loop
            while True:
                self.clear_screen()
                self.show_title()
                self.show_main_menu()
                
                choice = Prompt.ask("Choose an option", choices=["0", "1", "2", "3", "4", "5", "6"])
                
                if choice == "0":
                    self.console.print("[yellow]Goodbye![/yellow]")
                    return
                elif choice == "1":
                    self.show_collections()
                    collection = Prompt.ask("Enter collection name to view details (or press Enter to go back)", default="")
                    if collection:
                        self.show_collection_details(collection)
                        Prompt.ask("Press Enter to continue")
                elif choice == "2":
                    self.create_collection()
                    Prompt.ask("Press Enter to continue")
                elif choice == "3":
                    self.delete_collection()
                    Prompt.ask("Press Enter to continue")
                elif choice == "4":
                    self.view_document()
                    Prompt.ask("Press Enter to continue")
                elif choice == "5":
                    self.search_documents()
                    Prompt.ask("Press Enter to continue")
                elif choice == "6":
                    self.add_document()
                    Prompt.ask("Press Enter to continue")

    def create_collection(self):
        """Create a new collection."""
        self.clear_screen()
        self.show_title()
        
        self.console.print("[bold]Create New Collection[/bold]", style="blue")
        self.console.print()
        
        name = Prompt.ask("Collection name")
        if not name:
            self.console.print("[red]Collection name cannot be empty![/red]")
            return
            
        # Check if collection already exists
        existing_names = [col["name"] for col in self.collections]
        if name in existing_names:
            self.console.print(f"[red]Collection '{name}' already exists![/red]")
            return
            
        try:
            # Create the collection
            collection = self.client.create_collection(name=name)
            self.console.print(f"[green]Collection '{name}' created successfully![/green]")
            
            # Reload collections
            self.load_collections()
            
        except Exception as e:
            self.console.print(f"[red]Failed to create collection: {str(e)}[/red]")
            
    def delete_collection(self):
        """Delete a collection."""
        self.clear_screen()
        self.show_title()
        
        if not self.collections:
            self.console.print("[yellow]No collections to delete.[/yellow]")
            return
            
        self.console.print("[bold]Delete Collection[/bold]", style="blue")
        self.console.print()
        
        # Show available collections
        self.console.print("Available collections:")
        for i, col in enumerate(self.collections, 1):
            self.console.print(f"{i}. {col['name']} ({col['count']} documents)")
        self.console.print()
        
        name = Prompt.ask("Collection name to delete")
        if not name:
            return
            
        # Confirm deletion
        if not Confirm.ask(f"Are you sure you want to delete collection '{name}'? This cannot be undone."):
            return
            
        try:
            self.client.delete_collection(name=name)
            self.console.print(f"[green]Collection '{name}' deleted successfully![/green]")
            
            # Reload collections
            self.load_collections()
            
        except Exception as e:
            self.console.print(f"[red]Failed to delete collection: {str(e)}[/red]")
            
    def add_document(self):
        """Add a document to a collection."""
        self.clear_screen()
        self.show_title()
        
        if not self.collections:
            self.console.print("[yellow]No collections available. Create a collection first.[/yellow]")
            return
            
        self.console.print("[bold]Add Document[/bold]", style="blue")
        self.console.print()
        
        # Show available collections
        self.console.print("Available collections:")
        for i, col in enumerate(self.collections, 1):
            self.console.print(f"{i}. {col['name']} ({col['count']} documents)")
        self.console.print()
        
        collection_name = Prompt.ask("Collection name")
        if not collection_name:
            return
            
        # Find the collection
        collection_info = None
        for col in self.collections:
            if col["name"] == collection_name:
                collection_info = col
                break
                
        if not collection_info:
            self.console.print(f"[red]Collection '{collection_name}' not found.[/red]")
            return
            
        collection = collection_info["collection"]
        
        # Get document details
        doc_id = Prompt.ask("Document ID")
        if not doc_id:
            return
            
        document = Prompt.ask("Document text")
        if not document:
            return
            
        metadata_str = Prompt.ask("Metadata (JSON format, optional)", default="{}")
        
        try:
            metadata = json.loads(metadata_str) if metadata_str.strip() else {}
        except json.JSONDecodeError:
            self.console.print("[red]Invalid JSON format for metadata![/red]")
            return
            
        try:
            # Add the document
            collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[doc_id]
            )
            self.console.print(f"[green]Document '{doc_id}' added successfully![/green]")
            
            # Reload collections to update counts
            self.load_collections()
            
        except Exception as e:
            self.console.print(f"[red]Failed to add document: {str(e)}[/red]")
            
    def view_document(self):
        """View a complete document with all its details."""
        self.clear_screen()
        self.show_title()
        
        if not self.collections:
            self.console.print("[yellow]No collections available.[/yellow]")
            return
            
        self.console.print("[bold]View Document[/bold]", style="blue")
        self.console.print()
        
        # Show available collections
        self.console.print("Available collections:")
        for i, col in enumerate(self.collections, 1):
            self.console.print(f"{i}. {col['name']} ({col['count']} documents)")
        self.console.print()
        
        collection_name = Prompt.ask("Collection name")
        if not collection_name:
            return
            
        # Find the collection
        collection_info = None
        for col in self.collections:
            if col["name"] == collection_name:
                collection_info = col
                break
                
        if not collection_info:
            self.console.print(f"[red]Collection '{collection_name}' not found.[/red]")
            return
            
        collection = collection_info["collection"]
        
        # Show documents in the collection to help user pick
        self.console.print()
        try:
            result = collection.peek(limit=20)  # Show up to 20 documents
            
            if result['ids']:
                docs_table = Table(title=f"Documents in '{collection_name}'", box=box.ROUNDED)
                docs_table.add_column("ID", style="cyan", width=15)
                docs_table.add_column("Document Preview", style="white", width=60)
                
                for i, doc_id in enumerate(result['ids']):
                    document = result['documents'][i] if i < len(result['documents']) else ""
                    doc_preview = str(document)[:57] + "..." if len(str(document)) > 60 else str(document)
                    docs_table.add_row(str(doc_id), doc_preview)
                    
                self.console.print(docs_table)
                self.console.print()
        except Exception as e:
            self.console.print(f"[yellow]Could not load documents preview: {str(e)}[/yellow]")
            self.console.print()
        
        doc_id = Prompt.ask("Document ID")
        if not doc_id:
            return
            
        show_embedding = Confirm.ask("Show embedding vector?", default=False)
        
        try:
            # Get the specific document
            result = collection.get(
                ids=[doc_id],
                include=["documents", "metadatas", "embeddings"] if show_embedding else ["documents", "metadatas"]
            )
            
            if not result['ids']:
                self.console.print(f"[red]Document '{doc_id}' not found.[/red]")
                return
                
            self.console.print()
            self.console.print(Panel(f"[bold cyan]Document ID: {doc_id}[/bold cyan]", box=box.ROUNDED))
            self.console.print()
            
            # Display document text
            document = result['documents'][0] if result['documents'] else "N/A"
            self.console.print(Panel(
                Text(str(document), style="white"),
                title="[bold]Document Text[/bold]",
                box=box.ROUNDED,
                style="green"
            ))
            self.console.print()
            
            # Display metadata
            metadata = result['metadatas'][0] if result['metadatas'] else {}
            metadata_json = json.dumps(metadata, indent=2) if metadata else "{}"
            self.console.print(Panel(
                Text(metadata_json, style="yellow"),
                title="[bold]Metadata[/bold]",
                box=box.ROUNDED,
                style="blue"
            ))
            self.console.print()
            
            # Display embedding if requested
            if show_embedding:
                embeddings_data = result.get('embeddings')
                if embeddings_data is not None and len(embeddings_data) > 0:
                    embedding = embeddings_data[0]
                    if embedding is not None and len(embedding) > 0:
                        # Show embedding stats
                        import numpy as np
                        emb_array = np.array(embedding)
                        stats = f"Dimension: {len(embedding)}\n"
                        stats += f"Min: {emb_array.min():.6f}\n"
                        stats += f"Max: {emb_array.max():.6f}\n"
                        stats += f"Mean: {emb_array.mean():.6f}\n"
                        stats += f"Std: {emb_array.std():.6f}\n\n"
                        
                        # Show first 10 and last 10 values
                        if len(embedding) > 20:
                            stats += f"First 10 values: {embedding[:10]}\n"
                            stats += "...\n"
                            stats += f"Last 10 values: {embedding[-10:]}\n"
                        else:
                            stats += f"Values: {embedding}"
                        
                        self.console.print(Panel(
                            Text(stats, style="magenta"),
                            title="[bold]Embedding Vector[/bold]",
                            box=box.ROUNDED,
                            style="magenta"
                        ))
                        self.console.print()
                    else:
                        self.console.print("[yellow]No embedding available for this document.[/yellow]")
                        self.console.print()
                else:
                    self.console.print("[yellow]No embedding available for this document.[/yellow]")
                    self.console.print()
            
        except Exception as e:
            self.console.print(f"[red]Failed to retrieve document: {str(e)}[/red]")
    
    def search_documents(self):
        """Search documents in a collection."""
        self.clear_screen()
        self.show_title()
        
        if not self.collections:
            self.console.print("[yellow]No collections available.[/yellow]")
            return
            
        self.console.print("[bold]Search Documents[/bold]", style="blue")
        self.console.print()
        
        # Show available collections
        self.console.print("Available collections:")
        for i, col in enumerate(self.collections, 1):
            self.console.print(f"{i}. {col['name']} ({col['count']} documents)")
        self.console.print()
        
        collection_name = Prompt.ask("Collection name")
        if not collection_name:
            return
            
        # Find the collection
        collection_info = None
        for col in self.collections:
            if col["name"] == collection_name:
                collection_info = col
                break
                
        if not collection_info:
            self.console.print(f"[red]Collection '{collection_name}' not found.[/red]")
            return
            
        collection = collection_info["collection"]
        
        query = Prompt.ask("Search query")
        if not query:
            return
            
        try:
            n_results = int(Prompt.ask("Number of results", default="5"))
        except ValueError:
            n_results = 5
            
        try:
            # Perform the search
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if not results['ids'][0]:
                self.console.print("[yellow]No results found.[/yellow]")
                return
                
            # Display results
            results_table = Table(title=f"Search Results for '{query}'", box=box.ROUNDED)
            results_table.add_column("ID", style="cyan", width=15)
            results_table.add_column("Document", style="white", width=50)
            results_table.add_column("Distance", style="magenta", width=10)
            results_table.add_column("Metadata", style="green", width=25)
            
            for i, doc_id in enumerate(results['ids'][0]):
                document = results['documents'][0][i] if i < len(results['documents'][0]) else ""
                distance = f"{results['distances'][0][i]:.4f}" if i < len(results['distances'][0]) else ""
                metadata = results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}
                
                doc_content = str(document)[:47] + "..." if len(str(document)) > 50 else str(document)
                metadata_str = json.dumps(metadata) if metadata else "{}"
                metadata_str = metadata_str[:22] + "..." if len(metadata_str) > 25 else metadata_str
                
                results_table.add_row(str(doc_id), doc_content, distance, metadata_str)
                
            self.console.print(results_table)
            self.console.print()
            
        except Exception as e:
            self.console.print(f"[red]Search failed: {str(e)}[/red]")


def main():
    """Entry point for the application."""
    try:
        app = ChromaTUI()
        app.main_loop()
    except KeyboardInterrupt:
        Console().print("\n[yellow]Goodbye![/yellow]")
    except Exception as e:
        Console().print(f"\n[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    main()