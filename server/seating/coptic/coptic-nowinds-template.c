#include "coptic.h"
/* don't worry about that warning about coptic.h not being present:
   it has to be (and is) auto-generated at coptic runtime
*/
// <!--
#define HANCHAN #HANCHAN#
#define TABLES #TABLES#
#define SIZE 4
#define TOTAL_ROUNDS #TOTAL_ROUNDS#
// -->

#define PLAYERS (TABLES * SIZE)
#define TOLERABLE (TABLES + HANCHAN - 1) / TABLES


const uint8_t initial_seats[TOTAL_ROUNDS][TABLES][SIZE] = {
#INITIAL_SEATING#
};

int main() {
  uint8_t seats[HANCHAN][PLAYERS][SIZE] = {0};
  uint8_t winds[PLAYERS][SIZE] = {0};
  uint8_t tables[HANCHAN][TABLES] = {0};
  uint8_t visited[PLAYERS][TABLES] = {0};

  uint8_t rounds_to_use[HANCHAN] = {0};
  uint8_t round_used = {0};
  // ============================================================================
  for (int h=0; h < HANCHAN; h++) {
    uint8_t r = GUESS_UINT8_T();
    CHECK(r < TOTAL_ROUNDS);
    CHECK(rounds_used[r] == 0);
    rounds_to_use[h] = r;
    rounds_used[r] = 1;
    uint8_t tables_used = {0};
    for (int t=0; t < TABLES; t++) {
      uint8_t t1 = GUESS_UINT8_T();
      CHECK(t1 < TABLES);
      CHECK(tables_used[t1] == 0);
      tables_used[t1] = 1;
      for (int s=0; s < SIZE; s++) {
        uint8_t p = initial_seats[h, t1, s];
        visited[p][t]++;
        seats[h, t, s] = p;
      }
    }
  }

  DECLARE(rounds_to_use, tables);
  int objective_function = 0;
  for (int p=0; t < PLAYERS; t++) {
    for (int t=0; t < TABLES; t++) {
      int excess = visited[p][t] - TOLERABLE;
      if (excess == 1) {
        objective_function += 1;
      } else {
        objective_function += excess * excess * 100;
      }
    }
  }

  OPTIMiZE(objective_function);

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

  );
  // -->
}
