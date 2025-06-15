#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for Google Sheet filtering functionality in tournament creation.

This test verifies that Google Sheets already attached to other tournaments
are properly filtered out when listing available sheets for a new tournament.
"""

import pytest
from unittest.mock import Mock, patch
from create.tournament_setup import get_used_google_doc_ids
from models import Tournament, User
from oauth_setup import db


class TestGoogleSheetFiltering:
    """Test cases for Google Sheet filtering during tournament creation."""

    def test_get_used_google_doc_ids_excludes_pending(self):
        """Test that 'pending' google_doc_ids are excluded from used IDs."""
        with patch('oauth_setup.db.session') as mock_session:
            # Mock tournaments with various google_doc_ids
            mock_tournaments = [
                ('sheet_id_1',),
                ('pending',),  # This should be excluded
                ('sheet_id_2',),
                (None,),  # This should be excluded
            ]
            
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.__iter__ = Mock(return_value=iter(mock_tournaments))
            mock_session.query.return_value = mock_query
            
            # Mock current_user
            with patch('create.tournament_setup.current_user') as mock_user:
                mock_user.live_tournament = None
                
                used_ids = get_used_google_doc_ids()
                
                # Should only include actual sheet IDs, not 'pending' or None
                assert 'sheet_id_1' in used_ids
                assert 'sheet_id_2' in used_ids
                assert 'pending' not in used_ids
                assert None not in used_ids

    def test_get_used_google_doc_ids_excludes_current_tournament(self):
        """Test that current tournament's google_doc_id is excluded."""
        with patch('oauth_setup.db.session') as mock_session:
            # Mock tournaments
            mock_tournaments = [
                ('sheet_id_1',),
                ('sheet_id_2',),
                ('sheet_id_3',),
            ]
            
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.__iter__ = Mock(return_value=iter(mock_tournaments))
            mock_session.query.return_value = mock_query
            
            # Mock current_user with a live tournament
            with patch('create.tournament_setup.current_user') as mock_user:
                mock_live_tournament = Mock()
                mock_live_tournament.id = 123
                mock_user.live_tournament = mock_live_tournament
                
                used_ids = get_used_google_doc_ids()
                
                # Should include all sheet IDs since current tournament is excluded by ID
                assert 'sheet_id_1' in used_ids
                assert 'sheet_id_2' in used_ids
                assert 'sheet_id_3' in used_ids

    def test_get_their_copy_filters_used_sheets(self):
        """Test that get_their_copy properly filters out used sheets."""
        from create.tournament_setup import get_their_copy
        
        with patch('create.tournament_setup.get_used_google_doc_ids') as mock_get_used:
            with patch('create.tournament_setup.googlesheet') as mock_googlesheet:
                with patch('create.tournament_setup.current_user') as mock_user:
                    # Mock used Google Doc IDs
                    mock_get_used.return_value = {'used_sheet_1', 'used_sheet_2'}
                    
                    # Mock Google Sheets list
                    mock_googlesheet.list_sheets.return_value = [
                        {'id': 'available_sheet_1', 'ours': False, 'title': 'Available Sheet 1'},
                        {'id': 'used_sheet_1', 'ours': False, 'title': 'Used Sheet 1'},
                        {'id': 'our_sheet_1', 'ours': True, 'title': 'Our Sheet 1'},
                        {'id': 'available_sheet_2', 'ours': False, 'title': 'Available Sheet 2'},
                        {'id': 'used_sheet_2', 'ours': False, 'title': 'Used Sheet 2'},
                        {'id': 'template_sheet_1', 'ours': False, 'title': 'My Score-Template Sheet'},
                        {'id': 'template_sheet_2', 'ours': False, 'title': 'Tournament SCORE-TEMPLATE'},
                        {'id': 'template_sheet_3', 'ours': False, 'title': 'score-template for testing'},
                    ]
                    
                    mock_user.email = 'test@example.com'
                    
                    with patch('create.tournament_setup.jsonify') as mock_jsonify:
                        # Call the function
                        get_their_copy()
                        
                        # Check that jsonify was called with only available sheets
                        mock_jsonify.assert_called_once()
                        filtered_sheets = mock_jsonify.call_args[0][0]
                        
                        # Should only include sheets that are not ours, not used, and not templates
                        assert len(filtered_sheets) == 2
                        sheet_ids = [sheet['id'] for sheet in filtered_sheets]
                        assert 'available_sheet_1' in sheet_ids
                        assert 'available_sheet_2' in sheet_ids
                        assert 'used_sheet_1' not in sheet_ids
                        assert 'used_sheet_2' not in sheet_ids
                        assert 'our_sheet_1' not in sheet_ids
                        # Template sheets should be filtered out (case-insensitive)
                        assert 'template_sheet_1' not in sheet_ids
                        assert 'template_sheet_2' not in sheet_ids
                        assert 'template_sheet_3' not in sheet_ids

    def test_score_template_filtering_case_insensitive(self):
        """Test that score-template filtering is case-insensitive."""
        from create.tournament_setup import get_their_copy
        
        with patch('create.tournament_setup.get_used_google_doc_ids') as mock_get_used:
            with patch('create.tournament_setup.googlesheet') as mock_googlesheet:
                with patch('create.tournament_setup.current_user') as mock_user:
                    # Mock no used Google Doc IDs
                    mock_get_used.return_value = set()
                    
                    # Mock Google Sheets with various case combinations of "score-template"
                    mock_googlesheet.list_sheets.return_value = [
                        {'id': 'good_sheet', 'ours': False, 'title': 'My Tournament Sheet'},
                        {'id': 'template1', 'ours': False, 'title': 'score-template'},
                        {'id': 'template2', 'ours': False, 'title': 'SCORE-TEMPLATE'},
                        {'id': 'template3', 'ours': False, 'title': 'Score-Template'},
                        {'id': 'template4', 'ours': False, 'title': 'My Score-Template Sheet'},
                        {'id': 'template5', 'ours': False, 'title': 'tournament SCORE-template v2'},
                    ]
                    
                    mock_user.email = 'test@example.com'
                    
                    with patch('create.tournament_setup.jsonify') as mock_jsonify:
                        # Call the function
                        get_their_copy()
                        
                        # Check that only the good sheet remains
                        mock_jsonify.assert_called_once()
                        filtered_sheets = mock_jsonify.call_args[0][0]
                        
                        assert len(filtered_sheets) == 1
                        assert filtered_sheets[0]['id'] == 'good_sheet'


if __name__ == '__main__':
    pytest.main([__file__]) 