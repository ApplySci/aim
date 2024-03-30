import gspread
from oauth2client.service_account import ServiceAccountCredentials

TEMPLATE_ID = '1jVE1OTjFKSkxE4o3FhI5eWmD2XHYtAcP9LaUvFMQQ50'
KEYFILE = './fcm-admin.json'
MAX_HANCHAN = 20
MAX_TABLES = 20
SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive',
         ]


class GSP:
    def __init__(self) -> None:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            KEYFILE, SCOPE)
        self.client = gspread.authorize(creds)

    def get_results(live : gspread.spreadsheet.Spreadsheet) -> list:
        '''
        given a results spreadsheet, get the live results

        Args:
            live (gspread.spreadsheet.Spreadsheet): the gspread object for the workbook.

        Returns:
            list: the table of live results.

        '''
        return live.worksheet('results').get_all_values()


    def reduce_table_count(self, results, template, table_count: int) -> None:
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


    def reduce_hanchan_count(self, results, hanchan_count: int) -> None:
        # delete unnecessary rows in the RoundResults range
        ref_sheet: gspread.worksheet.Worksheet = \
            self.live_sheet.worksheet('reference')
        triggers = self.live_sheet.named_range('PublicationTriggers')
        first_row = triggers[0].row + hanchan_count + 1
        ref_sheet.delete_rows(first_row, triggers[-1].row)

        # delete unnecessary columns in the results sheet
        results.delete_columns(
            hanchan_count + 6,  MAX_HANCHAN + 5)


    def make_scoresheets(self, template, hanchan_count: int) -> None:
        for r in range(1, hanchan_count + 1):
            sheet = self.live_sheet.duplicate_sheet(
                template.id, 5, new_sheet_name=f'R{r}')
            # update cell B1 with the round number
            sheet.update([[r]], range_name='B1', raw=False)


    def set_permissions(self, owner, scorers, notify):
        permission = self.live_sheet.share(
            owner, perm_type='user', role='writer', notify=False)

        self.live_sheet.transfer_ownership(permission.json()['id'])
        for scorer in scorers:
            self.live_sheet.share(
                scorer, perm_type='user', role='writer', notify=notify)


    def create_new_results_googlesheet(
            self,
            table_count: int = 20,
            hanchan_count: int = 7,
            title: str = 'Riichi tournament results',
            owner: str = 'mj.apply.sci@gmail.com',
            scorers: list[str] = (),
            notify: bool = False,
            ) -> gspread.spreadsheet.Spreadsheet:
        '''

        Clones the scoring template workbook into a new workbook,
        adds a results page for each hanchan,
        and assigns write permissions to the scorers

        Args:
            table_count (int): the number of tables (1-MAX_TABLES) (= number of players divided by 4)
            hanchan_count (int): number of rounds (1-MAX_HANCHAN)
            title (str): title to be given to the new spreadsheet.
            owner (str): email address of the owner of the new spreadsheet.
            scorers (list[str]): list of email addresses to be given write permission.
            notify (bool): if true, sends a notification email to the owner and scorers

        Returns:
            gspread.spreadsheet.Spreadsheet: the new spreadsheet.

        '''

        self.live_sheet : gspread.spreadsheet.Spreadsheet = self.client.copy(
            TEMPLATE_ID, title=title, copy_comments=True,)

        template : gspread.worksheet.Worksheet = \
            self.live_sheet.worksheet('template')
        results: gspread.worksheet.Worksheet = \
            self.live_sheet.worksheet('results')

        if table_count < MAX_TABLES:
            self.reduce_table_count(results, template, table_count)

        if hanchan_count < MAX_HANCHAN:
            self.reduce_hanchan_count(results, hanchan_count)

        self.make_scoresheets(template, hanchan_count)

        self.set_permissions(owner, scorers, notify)
