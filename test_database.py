#!/usr/bin/env python3
"""
Test script for the database functionality
"""

import os
import sys
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database():
    """Test the database functionality"""
    print("🧪 Testing Database Functionality...")
    
    try:
        # Import our modules
        from database import db
        from backend import summarize_text_with_db, get_user_statistics, get_user_summary_history
        
        print("✅ Database module imported successfully")
        
        # Test user ID
        test_user_id = "test_user_001"
        
        # Test 1: Generate and save a summary
        print("\n📝 Test 1: Generating and saving a summary...")
        test_text = """
        Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines 
        that work and react like humans. Some of the activities computers with artificial intelligence are 
        designed for include speech recognition, learning, planning, and problem solving.
        
        AI has been around for decades, but recent advances in machine learning and deep learning have 
        made it more powerful and accessible than ever before. Machine learning algorithms can now process 
        vast amounts of data to identify patterns and make predictions with remarkable accuracy.
        
        The applications of AI are vast and growing, from virtual assistants like Siri and Alexa to 
        autonomous vehicles, medical diagnosis systems, and financial trading algorithms. As AI continues 
        to evolve, it will likely transform many industries and aspects of our daily lives.
        """
        
        result = summarize_text_with_db(
            text=test_text,
            style="bullet",
            user_id=test_user_id,
            document_name="AI Overview Test",
            document_type="text",
            file_size=len(test_text.encode('utf-8'))
        )
        
        if result['success']:
            print(f"✅ Summary generated and saved successfully!")
            print(f"   Summary ID: {result.get('summary_id')}")
            print(f"   Processing time: {result.get('processing_time')}s")
            print(f"   Word count: {result.get('word_count')} → {result.get('summary_word_count')}")
            print(f"   Quality score: {result.get('quality_metrics', {}).get('quality_score', 'N/A')}/100")
        else:
            print(f"❌ Summary generation failed: {result.get('error')}")
            return False
        
        # Test 2: Get user statistics
        print("\n📊 Test 2: Retrieving user statistics...")
        stats = get_user_statistics(test_user_id)
        print(f"✅ User statistics retrieved:")
        print(f"   Total summaries: {stats['total_summaries']}")
        print(f"   Total documents: {stats['total_documents']}")
        print(f"   Average quality: {stats['average_quality']}/100")
        print(f"   Favorite style: {stats['favorite_style']}")
        print(f"   Total words processed: {stats['total_words_processed']}")
        
        # Test 3: Get user summary history
        print("\n📚 Test 3: Retrieving user summary history...")
        history = get_user_summary_history(test_user_id, limit=5)
        print(f"✅ Retrieved {len(history)} summaries from history")
        
        for summary in history:
            print(f"   - {summary['document_name']} ({summary['summary_style']}) - {summary['created_at'][:10]}")
        
        # Test 4: Generate another summary with different style
        print("\n📝 Test 4: Generating another summary with different style...")
        result2 = summarize_text_with_db(
            text=test_text,
            style="abstract",
            user_id=test_user_id,
            document_name="AI Overview Test - Abstract",
            document_type="text",
            file_size=len(test_text.encode('utf-8'))
        )
        
        if result2['success']:
            print(f"✅ Second summary generated successfully!")
            print(f"   Summary ID: {result2.get('summary_id')}")
        else:
            print(f"❌ Second summary generation failed: {result2.get('error')}")
        
        # Test 5: Check updated statistics
        print("\n📊 Test 5: Checking updated statistics...")
        updated_stats = get_user_statistics(test_user_id)
        print(f"✅ Updated statistics:")
        print(f"   Total summaries: {updated_stats['total_summaries']}")
        print(f"   Total documents: {updated_stats['total_documents']}")
        
        print("\n🎉 All database tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found. Make sure you have set up your GEMINI_API_KEY.")
        print("   Create a .env file with: GEMINI_API_KEY=your_api_key_here")
    
    success = test_database()
    if success:
        print("\n🚀 Database integration is working correctly!")
        print("   You can now use the Streamlit app with full database functionality.")
    else:
        print("\n💥 Database integration test failed. Check the error messages above.")


