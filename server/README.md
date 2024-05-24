# Server-side stuff for the All-Ireland Mahjong Tournament app

## running a dev server locally
`flask --app tournament_setup.py run`

### installing
`pip install -r requirements.txt`

## Seating

Seating files are from Alice Miller's BoRAT - Breakout Room Allocation schedule Tool at http://breakoutroom.pythonanywhere.com/allocate/

This tool is based on "Breakout Group Allocation Schedules and the Social Golfer Problem with Adjacent Group Sizes", by Alice Miller, Matthew Barr, William Kavanagh, Ivaylo Valkov and Helen C. Purchase. Published in the Symmetry Journal, December 2020. https://doi.org/10.3390/sym13010013

I'm also starting to introduce solutions calculated with [Martin Lester's CoPTIC](https://dx.doi.org/10.1007/978-3-031-30820-8_13).

The [CoPTIC tool can be downloaded here](https://zenodo.org/records/7313352)

I'm using the specification set out in Martin's CoMaToSe paper, for fair seating. These criteria are met as closely as possible, given the number of players and number of rounds.

- no pair of players play together more than once
- no player sits at any one table more than once
- each player has each starting wind position the same number of times
- for each pair of players that do not play together, there is a floor
(pre-set at two or more) on the number of players who they both meet. For example, for 40 players and
seven rounds, for any pair of players that do not play together, there are at least **four** other players
that they both play against.
