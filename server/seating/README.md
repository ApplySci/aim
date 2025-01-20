# Seating for mahjong tournaments with 16-172 players.

For any given number of players, a seating arrangement has been generated for up to 15 hanchan without repeat meetups between players (where possible).

The seating arrangements are downloadable from [DOI:10.5281/zenodo.13971404](https://doi.org/10.5281/zenodo.13971404). This directory here on github contains the files that were used to create that download.

The seating allocation is designed to: minimize repeat meetups between players, & repeat visits to tables; balance wind allocations; and maximise the number of indirect meets between any pair of players via a third player.

Player IDs are a 1-based sequence: e.g. for a 48-player tournament, player IDs run 1-48

This dataset is built on Alice Miller's standard solutions to the Social Golfer Problem (see reference below): each such solution avoids repeat meetups between any pair of players.

We have reordered the data so that repeat vists to specific tables are minimised for each player. When we have taken a subset of the data, this has been done to maximise indirect meetups for pairs of players who do not meet directly. This indirect meetup criterion was developed by Martin Lester (see reference below). An indirect meetup is a player who plays each of players A and B, for players A and B who do not play each other,

After all these optimisations were carried out, we finally rearrange the order of players on each table in each hanchan, so that each player takes each seat number the same number of times. This is done so that tournament schedulers can, if they choose to, use pre-assigned starting winds for players, with seats 1-4 being East, South, West and North respectively.

## For Excel users

The Excel file contains one tab for each number of hanchan: the seating arrangements for 16-172 players are on each sheet. For example, sheet "10 h" contains seating arrangements for tournaments with 10 hanchan, for 16-172 players.

## For Python users

Each .py file contains all the seating for a specific number of hanchan. e.g. seats_8.py contains all the seating for mahjong tournaments with 8 hanchan, with 16-172 players.

Variable `seats` is a dict of seating arrangements. 
Each key is the number of players. 
The corresponding dict value is a list of hanchan. 
Each hanchan is a list of tables. 
Each table is a list of players, indexed from 1 upwards, in wind order (ESWN).

### To use:

Import the seats dictionary from the appropriate file:

```from seats_13 import seats```

Get seating for 60 players, 13 hanchan

```seating = seats[60]```

Access a specific hanchan (e.g., the first one)

```first_hanchan = seating[0]```

Access a specific table in a hanchan (e.g., the third table in the second hanchan)

`s = seating[1][2]`  
`print(f"Players at this table: East={s[0]}, South={s[1]}, West={s[2]}, North={s[3]}")`


The docstring for each .py file lists how many non-optimal occurrences happened, for each number of players:
- Winds: counts players who sit in any wind position too rarely or too often
- Tables: counts players who visit the same table more often than strictly necessary.
- Direct Meets: counts pairs of players who meet more than once across all hanchan.
- Indirect Meets: counts pairs of players who never play each other, and for whom there are too few other players who they each play.



# Detailed Statistics Files

The [statall.py](gams/statall.py) script generates detailed statistics files in the `stats/` directory. These files provide insights into the seating arrangements and highlight any non-optimal occurrences.


## Criteria for Warnings

### Winds:
Each player is expected to sit in each wind position a quarter of the time. Warnings are generated for each wind where a player is above or below that. e.g. for 11 hanchan, warnings are generated for any wind where a player sits 0 or 1 time; or more than three times.

### Tables: 
A warning is generated if the number of times a player visits the same table more than necessary. In almost all cases, that means visiting any table more than once. If there are more hanchan than tables, then it means visiting any table more than twice.

### Direct Meets:
Warnings are generated if pairs of players meet more than necessary across all hanchan. In almost all cases, that means meeting more than once. In rare edge cases (eg 16 players 6+ hanchan), it means meeting more than twice.

### Indirect Meets:
Warnings are generated if pairs of players never play each other, and there are too few other players who they each play (indirect meets), and there are more than four hanchan. The lowest acceptable number of indirect meets in such cases, is equal to the square root of the number of players. e.g for 36 players, each pair of players must have at least 6 indirect meets.

#### More on indirect meets:

For any two players A and B who don't meet directly (i.e. who never play against each other in a game), count the number of players who play both A and B. That's indirect meets. In general, more is better. And a little more specifically, if we take the minimum value of indirect_meets for all pairs of players who do not meet directly, then the higher that minimum value is, the better; and zero is very bad.

To take an extreme case to indicate why indirect meets might be informative, let's consider a 5 hanchan, 32 player tournament. Now, we know it's possible to schedule a 5 hanchan 16 player tournament with no repeats: a perfect fit, everyone plays everyone. So we could combine two of those arrangements, and have a situation where there were two separate groups of 16 players, and players in group A played everyone else in group A, but played no one in group B. (and vice-versa).

Obviously, that would be deeply unsatisfactory. So that's the extreme worst case, and one way to quantify why that's so bad, so that we can optimize *away* from it, is to measure indirect meets. Because, in this extreme case, there are 256 (16x16) pairs of players who have zero indirect meets between them.

#### More conceptually, we can frame it like this:

When A and B play each other, they have a chance to take points off each other directly, so we get some indication of how good A is, relative to B.

If they don't play each other directly, but both play quite a few other players, then we can judge how good A is relative to B, by looking at how well they perform in each case: 

if A always beats the shared third player, and B always loses to the shared third player, then we can expect that were A and B to finally meet, A would beat B, more often than B would beat A.

We want the rankings to reflect, as far as possible, the relationship between every pair of players, and so maximising the number of indirect meets is an appropriate objective.

NB I didn't work this out for myself. Martin Lester did the hard thinking, and published it in a paper (see reference below)


Created by Andrew ZP Smith (ZAPS) https://github.com/ApplySci/aim/

# References

Original SGP solutions from Alice Miller et al: [http://breakoutroom.pythonanywhere.com/allocate/](http://breakoutroom.pythonanywhere.com/allocate/)
"Breakout Group Allocation Schedules and the Social Golfer Problem with Adjacent Group Sizes", by Alice Miller, Matthew Barr, William Kavanagh, Ivaylo Valkov and Helen C. Purchase. [DOI:10.3390/sym13010013](https://dx.doi.org/10.3390/sym13010013), Symmetry, December 2020

Using additional mahjong-specific criteria devised & originally implemented by Martin Lester:
"Scheduling Reach Mahjong Tournaments Using Pseudoboolean Constraints" by Martin Mariusz Lester. [DOI:10.1007/978-3-030-80223-3_24](https://dx.doi.org/10.1007/978-3-030-80223-3_24) , Theory and Applications of Satisfiability Testing : SAT 2021 Lecture Notes in Computer Science, 2021, p. 349-358

My apologies to all for taking their beautiful combinatorial approaches and building a mess of brute force on top of them.

Smith, A. Z. (2024). Seating for Mahjong Tournaments (1.0.0) [Data set]. Zenodo. [DOI:10.5281/zenodo.13971404](https://doi.org/10.5281/zenodo.13971404)