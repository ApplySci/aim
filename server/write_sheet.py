# -*- coding: utf-8 -*-
"""
This does all the comms with, & handling of, the google scoresheet
"""

from datetime import datetime
import importlib
import random
import re

from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytz

from config import TEMPLATE_ID, OUR_EMAILS
from oauth_setup import KEYFILE

MAX_HANCHAN = 20
MAX_TABLES = 20
SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive',
         ]


class GSP:
    def __init__(self) -> None:
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            KEYFILE, SCOPE)
        self.client = gspread.authorize(self.creds)


    def get_sheet(self, id: str):
        return self.client.open_by_key(id)

    def get_raw_schedule(self, live : gspread.spreadsheet.Spreadsheet) -> list:
        return live.worksheet('schedule').get()[1:]

    def get_schedule(self, live : gspread.spreadsheet.Spreadsheet) -> list:
        '''
        get the timezone, the local start times, and the names of all the rounds.
        Convert all the datetimes to UTC, and standard ISO format
        '''
        vals : list  = self.get_raw_schedule(live)
        timezone_string = vals[0][2]
        tz = pytz.timezone(timezone_string)
        vals = vals[2:] # throw away the headers
        schedule : dict = {'timezone': timezone_string, 'rounds': []}
        for i in range(0, len(vals)):
            thisDatetime = datetime.strptime(vals[i][2], "%A %d %B %Y, %H:%M")
            utc_dt = tz.localize(thisDatetime).astimezone(pytz.UTC)
            schedule['rounds'].append({
                'id': vals[i][0],
                'name': vals[i][1],
                'start': utc_dt.isoformat(),
                })
        return schedule


    def get_seating(self, live : gspread.spreadsheet.Spreadsheet) -> list:
        return live.worksheet('seating').get(value_render_option=
            gspread.utils.ValueRenderOption.unformatted)[1:]


    def get_players(self, live : gspread.spreadsheet.Spreadsheet) -> list:
        return live.worksheet('players').get(value_render_option=
            gspread.utils.ValueRenderOption.unformatted)[3:]


    def count_completed_hanchan(self, live : gspread.spreadsheet.Spreadsheet) -> int:
        triggers = live.worksheet('GO LIVE').get('PublicationTriggers')
        done : int = 0 # number of completed hanchan
        for i in range(1, len(triggers)):
            if len(triggers[i]) < 3 or triggers[i][1] == '':
                break
            done = i
        return done


    def get_results(self, live : gspread.spreadsheet.Spreadsheet) -> list:
        return live.worksheet('results').get(
            value_render_option=gspread.utils.ValueRenderOption.unformatted)


    def get_table_results(
            self,
            round: int,
            live : gspread.spreadsheet.Spreadsheet) -> list:

        vals = live.worksheet(f'R{round}').get(value_render_option=
            gspread.utils.ValueRenderOption.unformatted)
        return vals


    def _reduce_table_count(self, results, template, table_count: int) -> None:
        # delete unnecessary rows in the results sheet
        results.delete_rows(2 + table_count * 4, 1 + MAX_TABLES * 4)
        # delete unnecessary rows in the template before copying it
        template.delete_rows(4 + table_count * 7, 3 + MAX_TABLES * 7)
        # fix the formula for the checksum total
        formula = template.acell(
            'G2', value_render_option='FORMULA').value
        template.update(
            [[formula[0 : formula.find('#REF!') - 1] + ')',],],
            range_name='G2',
            raw=False
            )


    def list_sheets(self, user_email : str, max_retries=3, retry_delay=5) -> list[dict]:
        '''
        Return the list of sheets that the user has access to, with titles,
        and a boolean flag to indicate whether WE (server admin) are the owner.

        Args:
            user_email (str): gmail address of the user whose sheets we must list
            max_retries (int): maximum number of retry attempts
            retry_delay (int): delay in seconds between retries

        Returns:
            list[dict]: {id: sheet.id, title: sheet.title, ours: true if WE own it}

        '''
        for attempt in range(max_retries):
            try:
                sheet_dict: list = self.client.list_spreadsheet_files()
                out = []
                for one in sheet_dict:
                    ours = False
                    this_user_can_see_this_sheet: bool = False
                    try:
                        sheet = self.client.open_by_key(one['id'])
                        details: dict = {
                            'id': one['id'],
                            'title': sheet.title,
                        }
                        try:
                            perms = sheet.list_permissions()
                            for perm in perms:
                                if perm['emailAddress'] == user_email:
                                    this_user_can_see_this_sheet = True
                                if perm['role'] == 'owner':
                                    ours = perm['emailAddress'] in OUR_EMAILS
                        except:
                            ours = False
                        if this_user_can_see_this_sheet:
                            details['ours'] = ours
                            out.append(details)
                    except APIError as e:
                        print(f"Error accessing sheet {one['id']}: {str(e)}")
                        continue
                return out
            except APIError as e:
                if attempt < max_retries - 1:
                    print(f"API Error: {str(e)}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"Max retries reached. Unable to list sheets: {str(e)}")
                    return []


    def _reduce_hanchan_count(self, results, hanchan_count: int) -> None:
        # delete unnecessary rows in the RoundResults range
        ref_sheet: gspread.worksheet.Worksheet = \
            self.live_sheet.worksheet('GO LIVE')
        triggers = self.live_sheet.named_range('PublicationTriggers')
        first_row = triggers[0].row + hanchan_count + 1
        ref_sheet.delete_rows(first_row, triggers[-1].row)

        # delete unnecessary columns in the results sheet
        results.delete_columns(
            hanchan_count + 6,  MAX_HANCHAN + 5)


    def _reduce_players(self, table_count: int) -> None:
        player_count = table_count * 4
        sheet = self.live_sheet.worksheet('players')
        sheet.delete_rows(4 + player_count, 3 + MAX_TABLES * 4)
        # randomise the seating. We expect organisers to do their own
        # randomising though. These are just placeholders, really
        seats = list(range(1, player_count + 1))
        random.shuffle(seats)
        seats = [[seat] for seat in seats]
        sheet.update(f'A4:A{player_count + 3}', seats)


    def _duplicate_hanchan_table(self, sheet, table_count):
        extra_rows = 7 * (table_count - 1)
        sheet.insert_rows([['']] * extra_rows, 10)

        body = {
            "requests": [
                {
                    "copyPaste": {
                        "source": {
                            "sheetId": sheet.id,
                            "startRowIndex": 3,
                            "endRowIndex": 10,
                        },
                        "destination": {
                            "sheetId": sheet.id,
                            "startRowIndex": 10,
                            "endRowIndex": 10 + extra_rows,
                        },
                    }
                },
            ],
        }
        res = self.live_sheet.batch_update(body)


    def _fix_score_checksum(self, sheet, table_count):
        sum_formula = "=ROUND(SUMSQ("
        plus = ""
        for i in range(table_count):
            sum_formula += f"{plus}g{i*7+9}"
            plus = "+"
        sum_formula += "),4)"
        sheet.update([[sum_formula]], range_name="G2", raw=False)


    def _make_scoresheets(
            self,
            template,
            hanchan_count: int,
            table_count: int) -> None:
        sheetname_to_copy = template.id
        for r in range(1, hanchan_count + 1):
            sheet = self.live_sheet.duplicate_sheet(
                sheetname_to_copy, 6, new_sheet_name=f'R{r}')
            # update cell B1 with the round number
            sheet.update([[r]], range_name='B1', raw=False)
            if r == 1:
                self._duplicate_hanchan_table(sheet, table_count)
                self._fix_score_checksum(sheet, table_count)
                sheetname_to_copy = sheet.id


    def _set_permissions(self, owner : str, scorers, notify : bool) -> None:
        '''
        grants Google Sheet write permissions to the new scorers


        Args:
            owner (str): email address of the new owner
            scorers (List<str>): email addresses of others to be given write permission
            notify (bool): whether to send a notification email to the scorers, with link to the sheet

        Returns:
            list: the table of live results.

        '''
        # permission =
        self.live_sheet.share(
            email_address=owner,
            perm_type='user',
            role='writer',
            notify=True,
            )

        # email regex is deliberately overly permissive,
        # because it's better to have false positives than false negatives
        pattern = r'..*\@..*\....*'
        for scorer in scorers:
            if re.match(pattern, scorer):
                if notify:
                    self.live_sheet.share(
                        scorer,
                        perm_type='user',
                        role='writer',
                        notify=notify,
                        email_message=f"{owner} has nominated you as a scorer " \
                            "for their mahjong tournament. This is the google " \
                            "scoring spreadsheet that will be used. " \
                            "See the README sheet to find out how to use it."
                        )
                else:
                    self.live_sheet.share(
                        scorer,
                        perm_type='user',
                        role='writer',
                        )
        #
        # Google prevents us from transferring ownership of a sheet.
        # So the line below, has been commented out, because it doesn't work.
        # I've kept it here, because I hope that someday, we will be able
        # to do this.
        #
        # self.live_sheet.transfer_ownership(permission.json()['id'])


    def _set_seating(self, table_count: int, hanchan_count: int) -> None:
        '''
        Reads in our pre-calculated seating plan for this size of tournament

        Args:
            table_count (int): number of tables (players divided by 4)
            hanchan_count (int): number of rounds

        Returns:
            None

        '''
        player_count = table_count * 4
        seats = importlib.import_module(
            f"seating.seats_{hanchan_count}").seats[player_count]
        destcells = []
        for round in range(0, hanchan_count):
            for table in range(0, table_count):
                destcells.append([round+1, table+1, *seats[round][table]])

        self.live_sheet.worksheet('seating').batch_update(
            [{'range': f'A2:F{table_count*hanchan_count+1}',
              'values': destcells,
              }]
            )


    def _set_schedule(self, hanchan_count: int, timezone : str,
                      start_times : list[str], template : str,
                      ):

        sheet: gspread.worksheet.Worksheet = self.live_sheet.worksheet(
            'schedule')
        sheet.update([[timezone]], range_name='C2', raw=True)
        starts : list[list[str]] =  [
            [template.replace('?', f'{x+1}'),
             start_times[x].replace('T', ' '),
            ] for x in range(hanchan_count)]
        sheet.update(f'B4:C{3+hanchan_count}', starts, raw=False)
        sheet.delete_rows(4 + hanchan_count, 3 + MAX_HANCHAN)


    def delete_sheet(self, doc_id: str) -> None:
        self.client.del_spreadsheet(doc_id)


    def create_new_results_googlesheet(
            self,
            table_count: int = 10,
            hanchan_count: int = 7,
            title: str = 'Riichi tournament results',
            owner: str = 'mj.apply.sci@gmail.com',
            scorers: list[str] = (),
            notify: bool = False,
            timezone: str = 'Dublin/Europe',
            start_times: list[str] = [],
            round_name_template: str = 'Round ?',
            ) -> str:
        '''

        Clones the scoring template workbook into a new workbook,
        adds a results page for each hanchan,
        and assigns write permissions to the scorers

        Args:
            table_count (int): the number of tables (1-20) (= number of players divided by 4)
            hanchan_count (int): number of rounds (1-20)
            title (str): title to be given to the new spreadsheet.
            owner (str): email address of the owner of the new spreadsheet.
            scorers (list[str]): list of email addresses to be given write permission.
            notify (bool): if true, sends a notification email to the owner and scorers
            start_times (list[str]): list of datetime strings
            timezone (str): timezone in pytz format eg Europe/Dublin

        Returns:
            gspread.spreadsheet.Spreadsheet: the new spreadsheet.

        '''

        if table_count < 1 or table_count > MAX_TABLES:
            raise ValueError(f'table_count must be between 1 and {MAX_TABLES}')

        if hanchan_count < 1 or hanchan_count > MAX_HANCHAN:
            raise ValueError(
                f'hanchan_count must be between 1 and {MAX_HANCHAN}')

        self.live_sheet : gspread.spreadsheet.Spreadsheet = self.client.copy(
            TEMPLATE_ID, title=title, copy_comments=True,)

        self._set_permissions(owner, ['mj.apply.sci@gmail.com'], False)

        template : gspread.worksheet.Worksheet = self.live_sheet.worksheet(
            'template')
        results: gspread.worksheet.Worksheet = self.live_sheet.worksheet(
            'results')

        if table_count < MAX_TABLES:
            self._reduce_players(table_count)
            self._reduce_table_count(results, template, table_count)

        if hanchan_count < MAX_HANCHAN:
            self._reduce_hanchan_count(results, hanchan_count)

        self._make_scoresheets(template, hanchan_count, table_count)

        self._set_seating(table_count, hanchan_count)

        self._set_schedule(hanchan_count, timezone, start_times,
                           round_name_template)

        self._set_permissions(owner, scorers, notify)

        return self.live_sheet.id


    def share_sheet(self, sheet_id: str, email: str, notify: bool = False):
        """
        Share a Google Sheet with a specific email address.

        Args:
            sheet_id (str): The ID of the Google Sheet to share.
            email (str): The email address of the user to share the sheet with.
            notify (bool): Whether to send a notification email to the user. Default is False.

        Returns:
            success: True (bool) if the share was successful, error message (str) otherwise.
        """
        try:
            sheet = self.get_sheet(sheet_id)
            sheet.share(
                email_address=email,
                perm_type='user',
                role='writer',
                notify=notify
            )
            return True
        except Exception as e:
            return f"Error sharing sheet: {str(e)}"


    def revoke_sheet_access(self, sheet_id: str, email: str):
        """
        Revoke a user's access to a Google Sheet.

        Args:
            sheet_id (str): The ID of the Google Sheet.
            email (str): The email address of the user whose access should be revoked.

        Returns:
            success: True (bool) if the access was successfully revoked, error message (str) otherwise.
        """
        try:
            drive_service = build('drive', 'v3', credentials=self.creds)
            
            permissions = drive_service.permissions().list(fileId=sheet_id).execute()
            permission_id = None
            for permission in permissions.get('permissions', []):
                if permission.get('emailAddress') == email:
                    permission_id = permission.get('id')
                    break

            if permission_id:
                drive_service.permissions().delete(
                    fileId=sheet_id,
                    permissionId=permission_id
                ).execute()
                return True
            else:
                return "User not found in sheet permissions"
        except HttpError as error:
            return f"An error occurred: {error}"
        except Exception as e:
            return f"Error revoking sheet access: {str(e)}"


    def get_sheet_users(self, sheet_id: str):
        """
        Get a list of users who have access to the specified Google Sheet.

        Args:
            sheet_id (str): The ID of the Google Sheet.

        Returns:
            list: A list of dictionaries containing user emails and their roles.
        """
        try:
            sheet = self.get_sheet(sheet_id)
            permissions = sheet.list_permissions()
            return [{'email': p['emailAddress'], 'role': p['role']} 
                    for p in permissions if 'emailAddress' in p]
        except Exception as e:
            return f"Error getting sheet users: {str(e)}"


googlesheet = GSP()

if __name__ == '__main__':
    out = googlesheet.create_new_results_googlesheet(
        table_count=10,
        hanchan_count=7,
        title='delete me',
        )

    print(out)

