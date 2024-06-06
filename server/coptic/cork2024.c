#include "coptic.h"
// #include "math.h"
// Originally built on Martin Lester's socialgolfer.c
// modified by Andrew ZP Smith

// <!--
#define TABLES 13
#define HANCHAN 7

#define SIZE 4
#define PERMUTATIONS 24
// the below is NOT the highest 2-path count allowable;
// it is instead the highest 2-path count we care about,
// so all higher 2-path counts are just counted in this final basket
#define MAX_2PATH_COUNT 10
// -->

// PERMUTATIONS = SIZE! (ie SIZE factorial)

#define PLAYERS (TABLES * SIZE)
#define MAX_WIND_REPEATS ((HANCHAN + SIZE - 1) / SIZE)
#define MAX_TABLE_REPEATS ((HANCHAN + TABLES - 1) / TABLES)

// one-third of the players you DO meet, should be in the middle of a 2-path to a player you don't meet
#define MIN_2_STEP_PATHS 1


// you will need to change this if you change SIZE
const uint8_t SEATING[PERMUTATIONS][SIZE] = {
  {0, 1, 2, 3},
  {0, 1, 3, 2},
  {0, 2, 1, 3},
  {0, 2, 3, 1},
  {0, 3, 1, 2},
  {0, 3, 2, 1},
  {1, 0, 2, 3},
  {1, 0, 3, 2},
  {1, 2, 0, 3},
  {1, 2, 3, 0},
  {1, 3, 0, 2},
  {1, 3, 2, 0},
  {2, 0, 1, 3},
  {2, 0, 3, 1},
  {2, 1, 0, 3},
  {2, 1, 3, 0},
  {2, 3, 0, 1},
  {2, 3, 1, 0},
  {3, 0, 1, 2},
  {3, 0, 2, 1},
  {3, 1, 0, 2},
  {3, 1, 2, 0},
  {3, 2, 0, 1},
  {3, 2, 1, 0}
};


int main() {
    uint8_t can_meet[PLAYERS][PLAYERS] = {0};
    uint8_t group[HANCHAN][PLAYERS] = {0};
    uint8_t seats[HANCHAN][TABLES][SIZE] = {0};
    uint8_t winds[PLAYERS][SIZE] = {0};
    uint8_t tables[PLAYERS][TABLES] = {0};
    int8_t do_meet[PLAYERS][PLAYERS] = {0};

    // For each pair of players, pick exactly one hanchan that they are allowed to meet in
    for (uint8_t p1 = 0; p1 < PLAYERS; p1++) {
        for (uint8_t p2 = p1+1; p2 < PLAYERS; p2++) {
            uint8_t m = GUESS_UINT8_T();
            CHECK(m >= 0 && m <= HANCHAN);
            can_meet[p1][p2] = m;
            can_meet[p2][p1] = m;
        }
    }


    // For each hannchan, for each player, pick a table.
    for (uint8_t h = 0; h < HANCHAN; h++) {
        for (uint8_t p = 0; p < PLAYERS; p++) {
            uint8_t t = GUESS_UINT8_T();
            CHECK(t >= 0 && t < TABLES);
            group[h][p] = t;
        }
    }


    // Check all TABLES same size.
    for (uint8_t t = 0; t < TABLES; t++) {
        for (uint8_t h = 0; h < HANCHAN; h++) {
            uint8_t total = 0;
            for (uint8_t p = 0; p < PLAYERS; p++) {
                total += (group[h][p] == t);
            }
            CHECK(total == SIZE);
        }
    }


    // Check socialisation.
    for (uint8_t p1 = 0; p1 < PLAYERS; p1++) {
        for (uint8_t p2 = p1+1; p2 < PLAYERS; p2++) {
            for (uint8_t h = 0; h < HANCHAN; h++) {
                CHECK((group[h][p1] != group[h][p2]) || (can_meet[p1][p2] == h));
            }
        }
    }


    // having got all that in place, now do wind assignments
    for (uint8_t h = 0; h < HANCHAN; h++) {
        for (uint8_t t = 0; t < TABLES; t++) {
            // do wind seating
            uint8_t wind_order = GUESS_UINT8_T();
            CHECK(wind_order >= 0 && wind_order < PERMUTATIONS);
            uint8_t s = 0;
            for (uint8_t p = 0; p < PLAYERS; p++) {
                if (group[h][p] == t) {
                    uint8_t seat = SEATING[wind_order][s++];
                    seats[h][t][seat] = p;
                    winds[p][seat]++;
                    tables[p][t]++;
                }
            }
        }
    }


    // check that no player is any one wind too often
    for (uint8_t p = 0; p < PLAYERS; p++) {
        for (uint8_t s = 0; s < SIZE; s++) {
            CHECK(winds[p][s] <= MAX_WIND_REPEATS);
        }
    }


    // check no player is on any one table too often
    for (uint8_t p = 0; p < PLAYERS; p++) {
        for (uint8_t t = 0; t < TABLES; t++) {
            CHECK(tables[p][t] <= MAX_TABLE_REPEATS);
        }
    }


    SATISFY();

    // <!--
    OUTPUT(

        printf("\n\nSEATING BY ROUND, BY TABLE\n");
        for (int h = 0; h < HANCHAN; h++) {
            for (int t = 0; t < TABLES; t++) {
                for (int s = 0; s < SIZE; s++) {
                    printf("%3d, ", seats[h][t][s]);
                }
                printf(";  ");
            }
            printf("\n");
        }

        printf("\n\n WIND COUNT BY PLAYER\n");

        for (uint8_t p = 0; p < PLAYERS; p++) {
            for (uint8_t s = 0; s < SIZE; s++) {
                printf("%3d, ",  winds[p][s]);
           }
           printf("\n");
       }


        printf("\n\n TABLE COUNT BY PLAYER\n");

        for (uint8_t p = 0; p < PLAYERS; p++) {
            for (uint8_t t = 0; t < TABLES; t++) {
                printf("%3d, ",  tables[p][t]);
           }
           printf("\n");
       }

        printf("\n\n MEET COUNT BY PLAYER (negative = count of length-2 paths)\n");

    // calculate second-order connections:
    // wherever player A doesn't meet player B, do they meet some player
    //   who also meets player B?

    // check which players meet each other
    for (uint8_t h = 0; h < HANCHAN; h++) {
        for (uint8_t t = 0; t < TABLES; t++) {
            for (uint8_t s1 = 0; s1 < SIZE; s1++) {
                for (uint8_t s2 = s1 + 1; s2 < SIZE; s2++) {
                    do_meet[ seats[h][t][s1] ][ seats[h][t][s2] ]++;
                    do_meet[ seats[h][t][s2] ][ seats[h][t][s1] ]++;
                }
            }
        }
    }


    int path1 = 0;
    uint8_t path2[MAX_2PATH_COUNT + 1] = {0};

    for (uint8_t p1 = 0; p1 < PLAYERS; p1++) {
        for (uint8_t p2 = p1 + 1; p2 < PLAYERS; p2++) {
            if (do_meet[p1][p2] == 0) {
                // these two players haven't met, so find the number of paths of length 2 between them
                int paths = 0;
                for (uint8_t p3 = 0; p3 < PLAYERS; p3++) {
                    if (do_meet[p1][p3] > 0 && do_meet[p2][p3] > 0) {
                        paths++;
                    }
                }
                // CHECK(paths >= MIN_2_STEP_PATHS);
                do_meet[p1][p2] = -paths;
                if (paths > MAX_2PATH_COUNT) paths = MAX_2PATH_COUNT;
                path2[paths]++;
            } else {
                path1++;
            }
        }
    }

        for (uint8_t p1 = 0; p1 < PLAYERS; p1++) {
            for (uint8_t p2 = p1 + 1; p2 < PLAYERS; p2++) {
                printf("%3d, ",  do_meet[p1][p2]);
            }
            printf("\n");
        }

        printf("\n\n PATH LENGTHS\n");
        printf("%d total unique player pairs\n", PLAYERS * (PLAYERS - 1) / 2);
        printf("%3d player-pairs who play each other\n", path1);
        for (int i = 0; i < MAX_2PATH_COUNT; i++) {
            printf("%3d player-pairs with %3d length-2 paths\n", path2[i], i);
        }
        printf("%3d player-pairs with %3d+ length-2 paths\n", path2[MAX_2PATH_COUNT], MAX_2PATH_COUNT);
    );
    // -->

}
