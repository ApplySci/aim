# -*- coding: utf-8 -*-
"""
Test cases for archiving tournaments using Google Sheet as authoritative source.

This test verifies that the archive process correctly reads player data from
Google Sheets rather than Firebase, especially important after table reductions.
"""

import pytest
import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from models import Tournament, ArchivedPlayer, TournamentPlayer
from operations.archive import archive_tournament


def test_archive_uses_google_sheet_for_players():
    """Test that archiving uses Google Sheet data as authoritative source for players."""
    
    # Mock Google Sheet data (authoritative) - player 41 exists with correct registration_id
    google_sheet_players = [
        ["1", "1", "Player 1"],
        ["2", "2", "Player 2"], 
        ["41", "42", "Substitute Player"],  # This is the correct data
    ]
    
    # Mock Firebase data (potentially stale) - different from Google Sheet
    firebase_players_data = {
        "players": [
            {"seating_id": "1", "registration_id": "1", "name": "Player 1"},
            {"seating_id": "2", "registration_id": "2", "name": "Player 2"},
            {"seating_id": None, "registration_id": "42", "name": "Substitute Player"},  # Stale data
        ]
    }
    
    # Mock other Firebase data
    tournament_data = {
        "title": "Test Tournament",
        "scores": {},
        "ranking": {},
        "seating": {}
    }
    
    # Mock tournament object
    tournament = Mock(spec=Tournament)
    tournament.id = 9
    tournament.firebase_doc = "test_tournament"
    tournament.google_doc_id = "test_sheet_id"
    
    with patch('operations.archive.firestore_client') as mock_firestore:
        # Mock main tournament document
        mock_tournament_ref = Mock()
        mock_tournament_doc = Mock()
        mock_tournament_doc.to_dict.return_value = tournament_data
        mock_tournament_ref.get.return_value = mock_tournament_doc
        
        # Mock v3 subcollection documents
        mock_v3_collection = Mock()
        
        # Mock Firebase players doc (this should NOT be used)
        mock_players_doc = Mock()
        mock_players_doc.get.return_value.to_dict.return_value = firebase_players_data
        
        # Mock other docs
        mock_ranking_doc = Mock()
        mock_ranking_doc.get.return_value.to_dict.return_value = {}
        mock_scores_doc = Mock()
        mock_scores_doc.get.return_value.to_dict.return_value = {}
        mock_seating_doc = Mock()
        mock_seating_doc.get.return_value.to_dict.return_value = {}
        
        def mock_document(name):
            return {
                "players": mock_players_doc,
                "ranking": mock_ranking_doc,
                "scores": mock_scores_doc,
                "seating": mock_seating_doc
            }[name]
        
        mock_v3_collection.document.side_effect = mock_document
        mock_tournament_ref.collection.return_value = mock_v3_collection
        mock_firestore.collection.return_value.document.return_value = mock_tournament_ref
        
        # Mock Google Sheet access
        with patch('operations.archive.googlesheet') as mock_googlesheet:
            mock_sheet = Mock()
            mock_googlesheet.get_sheet.return_value = mock_sheet
            mock_googlesheet.get_players.return_value = google_sheet_players
            
            # Mock database session
            with patch('operations.archive.db.session') as mock_session:
                mock_session.query.return_value.filter_by.return_value.first.return_value = None
                
                # Mock batch operations
                mock_batch = Mock()
                mock_firestore.batch.return_value = mock_batch
                
                # Run the archive function
                result = archive_tournament(tournament)
                
                # Verify it succeeded
                assert result is not False
                assert isinstance(result, dict)
                
                # Verify Google Sheet was accessed
                mock_googlesheet.get_sheet.assert_called_once_with("test_sheet_id")
                mock_googlesheet.get_players.assert_called_once_with(mock_sheet)
                
                # Verify TournamentPlayer was created with correct data from Google Sheet
                # The substitute should have seating_id="41" and registration_id="42"
                tournament_player_calls = [
                    call for call in mock_session.add.call_args_list 
                    if call[0] and isinstance(call[0][0], TournamentPlayer)
                ]
                
                # Should have 3 TournamentPlayer objects added
                assert len(tournament_player_calls) == 3
                
                # Find the substitute player
                substitute_player = None
                for call in tournament_player_calls:
                    tp = call[0][0]
                    if tp.registration_id == "42":
                        substitute_player = tp
                        break
                
                assert substitute_player is not None
                assert substitute_player.seating_id == "41"  # From Google Sheet, not None from Firebase
                assert substitute_player.registration_id == "42"


def test_archive_fallback_to_firebase_on_sheet_error():
    """Test that archiving falls back to Firebase if Google Sheet is inaccessible."""
    
    # Mock Firebase data
    firebase_players_data = {
        "players": [
            {"seating_id": "1", "registration_id": "1", "name": "Player 1"},
        ]
    }
    
    tournament_data = {"title": "Test Tournament"}
    
    # Mock tournament object
    tournament = Mock(spec=Tournament)
    tournament.id = 9
    tournament.firebase_doc = "test_tournament"
    tournament.google_doc_id = "inaccessible_sheet_id"
    
    with patch('operations.archive.firestore_client') as mock_firestore:
        # Mock Firestore setup (same as above)
        mock_tournament_ref = Mock()
        mock_tournament_doc = Mock()
        mock_tournament_doc.to_dict.return_value = tournament_data
        mock_tournament_ref.get.return_value = mock_tournament_doc
        
        mock_v3_collection = Mock()
        mock_players_doc = Mock()
        mock_players_doc.get.return_value.to_dict.return_value = firebase_players_data
        
        mock_v3_collection.document.return_value = mock_players_doc
        mock_tournament_ref.collection.return_value = mock_v3_collection
        mock_firestore.collection.return_value.document.return_value = mock_tournament_ref
        
        # Mock Google Sheet to raise an exception
        with patch('operations.archive.googlesheet') as mock_googlesheet:
            mock_googlesheet.get_sheet.side_effect = Exception("Sheet not accessible")
            
            with patch('operations.archive.db.session') as mock_session:
                mock_session.query.return_value.filter_by.return_value.first.return_value = None
                
                mock_batch = Mock()
                mock_firestore.batch.return_value = mock_batch
                
                # Run the archive function
                result = archive_tournament(tournament)
                
                # Should still succeed using Firebase fallback
                assert result is not False
                assert isinstance(result, dict)
                
                # Verify Google Sheet was attempted
                mock_googlesheet.get_sheet.assert_called_once_with("inaccessible_sheet_id")
                
                # Verify Firebase players doc was accessed as fallback
                mock_players_doc.get.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__]) 