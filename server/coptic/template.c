#include "coptic.h"
/* don't worry about that warning about coptic.h not being present:
   it has to be (and is) auto-generated at coptic runtime
*/
// <!--
#define HANCHAN #HANCHAN#
#define TABLES #TABLES#
#define SIZE 4
#define PERMUTATIONS 24
#define TOTAL_ROUNDS #TOTAL_ROUNDS#
// -->

#define MAX_WIND_REPEATS ( (HANCHAN + 3) / 4)
#define PLAYERS (TABLES * SIZE)

const uint8_t rounds_to_use[HANCHAN] = {#ROUNDS_TO_USE#};

const uint8_t initial_seats[TOTAL_ROUNDS][TABLES][SIZE] = {
#INITIAL_SEATING#
};

// you will need to change this if you change SIZE
const uint8_t SEATING[PERMUTATIONS][SIZE] = {
    {0, 1, 2, 3}, {0, 1, 3, 2}, {0, 2, 1, 3}, {0, 2, 3, 1}, {0, 3, 1, 2},
    {0, 3, 2, 1}, {1, 0, 2, 3}, {1, 0, 3, 2}, {1, 2, 0, 3}, {1, 2, 3, 0},
    {1, 3, 0, 2}, {1, 3, 2, 0}, {2, 0, 1, 3}, {2, 0, 3, 1}, {2, 1, 0, 3},
    {2, 1, 3, 0}, {2, 3, 0, 1}, {2, 3, 1, 0}, {3, 0, 1, 2}, {3, 0, 2, 1},
    {3, 1, 0, 2}, {3, 1, 2, 0}, {3, 2, 0, 1}, {3, 2, 1, 0}};

int main() {
  uint8_t seats[HANCHAN][PLAYERS][SIZE] = {0};
  uint8_t winds[PLAYERS][SIZE] = {0};
  uint8_t tables[PLAYERS][TABLES] = {0};

  // at each table, order the players in a random order
  for (uint8_t h = 0; h < HANCHAN; h++) {
    for (uint8_t t = 0; t < TABLES; t++) {
      uint8_t wind_order = GUESS_UINT8_T();
      CHECK(wind_order < PERMUTATIONS);
      for (uint8_t s = 0; s < SIZE; s++) {
        uint8_t seat = SEATING[wind_order][s];
        uint8_t p = initial_seats[rounds_to_use[h]][t][s];
        seats[h][t][seat] = p;
        winds[p][seat]++;
      }
    }
  }

  // check that no player is any one wind too often
  for (uint8_t p = 0; p < PLAYERS; p++) {
    for (uint8_t s = 0; s < SIZE; s++) {
      CHECK(winds[p][s] <= MAX_WIND_REPEATS);
    }
  }

  // ============================================================================
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
          printf("%3d, ", winds[p][s]);
        }
        printf("\n");
      }

  );
  // -->
}
