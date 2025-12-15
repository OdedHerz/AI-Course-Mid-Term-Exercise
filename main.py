"""
Orchestrator - Main entry point for the multi-agent query system

This orchestrator coordinates the routing, needle, and summary agents to
provide a unified interface for querying the insurance claim.
"""

import sys
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from Agents.routing_agent import RoutingAgent
from Agents.needle_agent import NeedleAgent
from Agents.summary_agent import SummaryAgent
from Config import config


class ClaimQueryOrchestrator:
    """
    Main orchestrator that coordinates all agents to answer user queries.
    """
    
    def __init__(self):
        """Initialize all agents."""
        print("[ORCHESTRATOR] Initializing multi-agent system...")
        
        self.routing_agent = RoutingAgent()
        print("[ORCHESTRATOR] - Routing agent ready")
        
        self.needle_agent = NeedleAgent()
        print("[ORCHESTRATOR] - Needle agent ready")
        
        self.summary_agent = SummaryAgent()
        print("[ORCHESTRATOR] - Summary agent ready")
        
        print("[ORCHESTRATOR] All agents initialized successfully!\n")
    
    def query(self, user_query: str, verbose: bool = True) -> dict:
        """
        Process a user query through the multi-agent system.
        
        Args:
            user_query: The user's question
            verbose: Whether to print detailed execution logs
            
        Returns:
            dict: {
                "query": original query,
                "route": "summary" or "needle",
                "answer": the generated answer,
                "sources": list of sources used,
                "metadata": additional information
            }
        """
        if verbose:
            print("=" * 70)
            print("INSURANCE CLAIM QUERY SYSTEM")
            print("=" * 70)
            print(f"\nUser Query: {user_query}\n")
        
        # Step 1: Route the query
        route = self.routing_agent.route(user_query)
        
        # Step 2: Execute appropriate agent
        if route == "summary":
            if verbose:
                print("\n[ORCHESTRATOR] Routing to SUMMARY AGENT...")
            result = self.summary_agent.answer_query(user_query)
            agent_type = "summary"
        else:  # needle
            if verbose:
                print("\n[ORCHESTRATOR] Routing to NEEDLE AGENT...")
            result = self.needle_agent.answer_query(user_query)
            agent_type = "needle"
        
        # Step 3: Format and return response
        response = {
            "query": user_query,
            "route": route,
            "agent": agent_type,
            "answer": result["answer"],
            "sources": result["sources"],
            "metadata": {
                "chunks_used": result.get("chunks_used", result.get("summaries_used", 0)),
                "parent_pages_used": result.get("parent_pages_used", 0),
                "agent_type": agent_type
            }
        }
        
        if verbose:
            print("\n" + "=" * 70)
            print("ANSWER")
            print("=" * 70)
            print(f"\n{response['answer']}\n")
            print("=" * 70)
            print("SOURCES")
            print("=" * 70)
            for source in response['sources']:
                print(f"  - Page {source['page']}: {source['header']}")
            
            # Show auto-merge info for needle queries
            if agent_type == "needle" and response['metadata'].get('parent_pages_used', 0) > 0:
                print(f"\n[AUTO-MERGE] Used {response['metadata']['parent_pages_used']} parent page(s) for additional context")
            
            print("=" * 70)
        
        return response
    
    def batch_query(self, queries: list) -> list:
        """
        Process multiple queries in batch.
        
        Args:
            queries: List of user questions
            
        Returns:
            list: List of response dictionaries
        """
        results = []
        
        for i, query in enumerate(queries, 1):
            print(f"\n{'='*70}")
            print(f"QUERY {i}/{len(queries)}")
            print('='*70)
            
            result = self.query(query, verbose=True)
            results.append(result)
        
        return results


def show_main_menu():
    """Display the main menu and return user choice."""
    print("\n" + "=" * 70)
    print("INSURANCE CLAIM QUERY SYSTEM - MAIN MENU")
    print("=" * 70)
    print("\n1. Ask a Question")
    print("2. Create/Recreate Indexing")
    print("3. RAGAS Evaluation")
    print("4. Exit Program")
    print("\n" + "=" * 70)
    
    while True:
        choice = input("\nSelect an option (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            return choice
        print("[ERROR] Invalid choice. Please enter 1, 2, 3, or 4.")


def show_evaluation_submenu():
    """Display the RAGAS evaluation submenu and return user choice."""
    print("\n" + "=" * 70)
    print("RAGAS EVALUATION - SELECT MODE")
    print("=" * 70)
    print("\n1. Run Query Phase (collect agent responses)")
    print("2. Run Evaluation Phase (judge with Gemini)")
    print("3. Run Full Evaluation (both phases + PDF report)")
    print("4. Generate PDF Report (from existing results)")
    print("5. Back to Main Menu")
    print("6. Exit Program")
    print("\n" + "=" * 70)
    
    while True:
        choice = input("\nSelect an option (1-6): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6']:
            return choice
        print("[ERROR] Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")


def ask_questions_mode(orchestrator):
    """Interactive question-asking mode."""
    print("\n" + "=" * 70)
    print("QUESTION MODE")
    print("=" * 70)
    print("\nYou can now ask questions about the insurance claim.")
    print("Type 'menu' to return to main menu.")
    print("=" * 70)
    
    while True:
        try:
            user_input = input("\nYour question (or 'menu' to return): ").strip()
            
            if user_input.lower() in ['menu', 'exit', 'quit', 'back']:
                print("\n[SYSTEM] Returning to main menu...")
                break
            
            if not user_input:
                continue
            
            orchestrator.query(user_input, verbose=True)
            
        except KeyboardInterrupt:
            print("\n\n[SYSTEM] Returning to main menu...")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}\n")
            print("Please try again or type 'menu' to return to main menu.")


def create_indexing_mode():
    """Create or recreate all indexes with user confirmation."""
    # Calculate expected numbers from metadata
    try:
        with open(config.METADATA_PATH, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        num_pages = len(metadata)
        # Estimate chunks: each page ~1200-1900 chars, chunk size 300, overlap 40
        # Based on actual data: ~7 chunks per page on average
        estimated_chunks = num_pages * 7
        
        # Calculate actual estimated time based on pages
        estimated_minutes = max(1, num_pages // 2)
        estimated_cost = round(num_pages * 0.002, 2)  # Rough cost per page
    except Exception:
        # Fallback to default values if metadata can't be read
        num_pages = "?"
        estimated_chunks = "?"
        estimated_minutes = "1-2"
        estimated_cost = "0.02"
    
    print("\n" + "=" * 70)
    print("CREATE/RECREATE INDEXING")
    print("=" * 70)
    print("\nThis will:")
    print(f"  1. Generate embeddings for all document chunks (~{estimated_chunks} chunks)")
    print(f"  2. Generate embeddings for page summaries ({num_pages} summaries)")
    print("  3. Store all data in Supabase vector database")
    print("  4. Create local document store for parent pages")
    print("\nWARNING: This will overwrite existing indexes!")
    print(f"\nEstimated time: {estimated_minutes} minutes")
    print(f"API costs: ~${estimated_cost} (OpenAI embeddings)")
    print("\n" + "=" * 70)
    
    while True:
        confirm = input("\nDo you want to proceed? (Y/N): ").strip().upper()
        
        if confirm == 'N':
            print("\n[SYSTEM] Indexing cancelled. Returning to main menu...")
            return
        
        if confirm == 'Y':
            print("\n[SYSTEM] Starting indexing process...\n")
            
            try:
                # Import the main indexing orchestrator
                from Indexing.create_all_indexes import main as create_all_indexes
                
                # Run the complete indexing process (tables + data)
                needle_result, summary_result = create_all_indexes()
                
                # Check if indexing was successful
                if needle_result is None or summary_result is None:
                    print("\n[ABORTED] Indexing process failed.")
                    input("\nPress Enter to return to main menu...")
                    return
                
                print("\n" + "=" * 70)
                print("[SUCCESS] Indexing completed successfully!")
                print("=" * 70)
                input("\nPress Enter to return to main menu...")
                return
                
            except Exception as e:
                print(f"\n[ERROR] Indexing failed: {e}")
                print("\nPlease check:")
                print("  - OpenAI API key is valid")
                print("  - Supabase credentials are correct")
                print("  - Internet connection is working")
                input("\nPress Enter to return to main menu...")
                return
        
        print("[ERROR] Please enter Y or N.")


def run_query_phase_mode():
    """Run Phase 1: Query collection mode."""
    print("\n" + "=" * 70)
    print("PHASE 1: QUERY COLLECTION")
    print("=" * 70)
    print("\nThis will:")
    print("  1. Load test dataset (10 questions: 5 needle, 5 summary)")
    print("  2. Run queries through your RAG system")
    print("  3. Save results to query_results.json")
    print("\nEstimated time: 2-3 minutes")
    print("API costs: ~$0.05 (OpenAI agents)")
    print("\n" + "=" * 70)
    
    while True:
        confirm = input("\nDo you want to proceed? (Y/N): ").strip().upper()
        
        if confirm == 'N':
            print("\n[SYSTEM] Query phase cancelled. Returning to main menu...")
            return
        
        if confirm == 'Y':
            print("\n[SYSTEM] Starting query phase...\n")
            
            try:
                from Evaluation.evaluate import run_query_phase
                run_query_phase()
                
                print("\n" + "=" * 70)
                
                # Offer to continue to evaluation phase
                while True:
                    choice = input("\nDo you want to continue to Phase 2 (Evaluation)? (Y/N): ").strip().upper()
                    
                    if choice == 'Y':
                        print("\n[SYSTEM] Proceeding to Phase 2: Evaluation...\n")
                        run_evaluation_phase_mode()
                        return
                    elif choice == 'N':
                        print("\n[SYSTEM] Returning to main menu...")
                        return
                    else:
                        print("[ERROR] Please enter Y or N.")
                
            except FileNotFoundError as e:
                print(f"\n[ERROR] {e}")
                print("\nPlease ensure test_dataset.json exists in Evaluation/ folder")
                input("\nPress Enter to return to main menu...")
                return
            
            except Exception as e:
                print(f"\n[ERROR] Query phase failed: {e}")
                import traceback
                traceback.print_exc()
                input("\nPress Enter to return to main menu...")
                return
        
        print("[ERROR] Please enter Y or N.")


def run_evaluation_phase_mode():
    """Run Phase 2: Gemini evaluation mode."""
    print("\n" + "=" * 70)
    print("PHASE 2: GEMINI EVALUATION")
    print("=" * 70)
    print("\nThis will:")
    print("  1. Load query results from query_results.json")
    print("  2. Evaluate using 6 RAGAS metrics with Gemini")
    print("  3. Save evaluation scores")
    print("\nEstimated time: 2-3 minutes")
    print("API costs: ~$0.10 (Gemini evaluation)")
    print("\n" + "=" * 70)
    
    while True:
        confirm = input("\nDo you want to proceed? (Y/N): ").strip().upper()
        
        if confirm == 'N':
            print("\n[SYSTEM] Evaluation phase cancelled. Returning to main menu...")
            return
        
        if confirm == 'Y':
            print("\n[SYSTEM] Starting evaluation phase...\n")
            
            try:
                from Evaluation.evaluate import run_evaluation_phase
                run_evaluation_phase()
                
                print("\n" + "=" * 70)
                input("\nPress Enter to return to main menu...")
                return
                
            except FileNotFoundError as e:
                print(f"\n[ERROR] {e}")
                print("\nPlease run Phase 1 (Query Collection) first!")
                input("\nPress Enter to return to main menu...")
                return
            
            except ValueError as e:
                if "GOOGLE_AI_API_KEY" in str(e):
                    print(f"\n[ERROR] {e}")
                    print("\nPlease add to your .env file:")
                    print("  GOOGLE_AI_API_KEY=your_api_key_here")
                else:
                    print(f"\n[ERROR] Evaluation phase failed: {e}")
                input("\nPress Enter to return to main menu...")
                return
            
            except Exception as e:
                print(f"\n[ERROR] Evaluation phase failed: {e}")
                import traceback
                traceback.print_exc()
                input("\nPress Enter to return to main menu...")
                return
        
        print("[ERROR] Please enter Y or N.")


def run_full_evaluation_mode():
    """Run both phases sequentially."""
    print("\n" + "=" * 70)
    print("FULL EVALUATION (BOTH PHASES + PDF)")
    print("=" * 70)
    print("\nThis will:")
    print("  1. Load test dataset (10 questions: 5 needle, 5 summary)")
    print("  2. Run queries through your RAG system")
    print("  3. Evaluate using 6 RAGAS metrics with Gemini")
    print("  4. Generate JSON results + PDF report")
    print("\nEstimated time: 5-6 minutes")
    print("API costs: ~$0.15 (OpenAI + Gemini)")
    print("\n" + "=" * 70)
    
    while True:
        confirm = input("\nDo you want to proceed? (Y/N): ").strip().upper()
        
        if confirm == 'N':
            print("\n[SYSTEM] Full evaluation cancelled. Returning to main menu...")
            return
        
        if confirm == 'Y':
            print("\n[SYSTEM] Starting full evaluation...\n")
            
            try:
                from Evaluation.evaluate import run_full_evaluation
                run_full_evaluation()
                
                print("\n" + "=" * 70)
                input("\nPress Enter to return to main menu...")
                return
                
            except FileNotFoundError as e:
                print(f"\n[ERROR] {e}")
                print("\nPlease ensure test_dataset.json exists in Evaluation/ folder")
                input("\nPress Enter to return to main menu...")
                return
            
            except ValueError as e:
                if "GOOGLE_AI_API_KEY" in str(e):
                    print(f"\n[ERROR] {e}")
                    print("\nPlease add to your .env file:")
                    print("  GOOGLE_AI_API_KEY=your_api_key_here")
                else:
                    print(f"\n[ERROR] Full evaluation failed: {e}")
                input("\nPress Enter to return to main menu...")
                return
            
            except Exception as e:
                print(f"\n[ERROR] Full evaluation failed: {e}")
                import traceback
                traceback.print_exc()
                input("\nPress Enter to return to main menu...")
                return
        
        print("[ERROR] Please enter Y or N.")


def run_pdf_generation_mode():
    """Run PDF Report Generation mode."""
    print("\n" + "=" * 70)
    print("GENERATE PDF REPORT")
    print("=" * 70)
    print("\nThis will:")
    print("  1. Load existing evaluation_results.json")
    print("  2. Generate PDF report")
    print("\nEstimated time: < 10 seconds")
    print("No API costs (uses existing results)")
    print("\n" + "=" * 70)
    
    while True:
        confirm = input("\nDo you want to proceed? (Y/N): ").strip().upper()
        
        if confirm == 'N':
            print("\n[SYSTEM] PDF generation cancelled. Returning to evaluation menu...")
            return
        
        if confirm == 'Y':
            print("\n[SYSTEM] Generating PDF report...\n")
            
            try:
                from Evaluation.evaluate import generate_pdf_from_existing
                generate_pdf_from_existing()
                input("\nPress Enter to return to evaluation menu...")
                return
            
            except FileNotFoundError as e:
                print(f"\n[ERROR] {e}")
                print("\nPlease ensure evaluation_results.json exists in Evaluation/ folder")
                input("\nPress Enter to return to evaluation menu...")
                return
            
            except Exception as e:
                print(f"\n[ERROR] PDF generation failed: {e}")
                import traceback
                traceback.print_exc()
                input("\nPress Enter to return to evaluation menu...")
                return
        
        print("[ERROR] Please enter Y or N.")


def evaluation_menu_mode():
    """Handle the RAGAS evaluation submenu."""
    while True:
        choice = show_evaluation_submenu()
        
        if choice == '1':
            run_query_phase_mode()
        
        elif choice == '2':
            run_evaluation_phase_mode()
        
        elif choice == '3':
            run_full_evaluation_mode()
        
        elif choice == '4':
            run_pdf_generation_mode()
        
        elif choice == '5':
            print("\n[SYSTEM] Returning to main menu...")
            break
        
        elif choice == '6':
            print("\n" + "=" * 70)
            print("Thank you for using the Insurance Claim Query System!")
            print("=" * 70)
            print()
            exit(0)


# Example usage and interactive mode
if __name__ == "__main__":
    import sys
    
    # Check if running in test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode with example queries
        orchestrator = ClaimQueryOrchestrator()
        
        test_queries = [
            "What time did the collision occur?",
            "Summarize the events that led to the claim.",
            "What was Sarah Mitchell's blood pressure during assessment?",
            "Who was determined to be at fault?",
            "What was the license plate of the Toyota Camry?",
            "Give me an overview of the medical treatment.",
            "How many feet were the skid marks?",
            "What was the total estimated claim value?"
        ]
        
        orchestrator.batch_query(test_queries)
    else:
        # Interactive menu mode
        print("\n" + "=" * 70)
        print("INSURANCE CLAIM MULTI-AGENT QUERY SYSTEM")
        print("=" * 70)
        print("\nInitializing system...")
        
        try:
            orchestrator = ClaimQueryOrchestrator()
            
            # Main menu loop
            while True:
                choice = show_main_menu()
                
                if choice == '1':
                    ask_questions_mode(orchestrator)
                
                elif choice == '2':
                    create_indexing_mode()
                
                elif choice == '3':
                    evaluation_menu_mode()
                
                elif choice == '4':
                    print("\n" + "=" * 70)
                    print("Thank you for using the Insurance Claim Query System!")
                    print("=" * 70)
                    print()
                    break
        
        except KeyboardInterrupt:
            print("\n\n[SYSTEM] Program interrupted. Goodbye!")
        except Exception as e:
            print(f"\n[ERROR] Fatal error: {e}")
            print("Please check your configuration and try again.")

