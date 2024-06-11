#include "coptic.h"
// #include "math.h"
// Originally built on Martin Lester's socialgolfer.c
// modified by Andrew ZP Smith

// <!--
#define HANCHAN 8
#define TABLES 8
#define SIZE 4
#define PERMUTATIONS 24
#define MAX_WIND_REPEATS 2
#define MAX_TABLE_REPEATS 2
#define IGNORE_H1 8
#define IGNORE_H2 9
// -->


#define PLAYERS (TABLES * SIZE)

const uint8_t initial_seats[10][8][4] = {
	{{0, 1, 2, 3},
	{4, 5, 6, 7},
	{8, 9, 10, 11},
	{12, 13, 14, 15},
	{16, 17, 18, 19},
	{20, 21, 22, 23},
	{24, 25, 26, 27},
	{28, 29, 30, 31}},

	{{0, 4, 8, 28},
	{1, 7, 18, 22},
	{3, 5, 10, 31},
	{15, 19, 21, 26},
	{12, 16, 20, 24},
	{2, 6, 17, 23},
	{11, 13, 25, 30},
	{9, 14, 27, 29}},

	{{0, 21, 27, 30},
	{1, 23, 26, 28},
	{3, 6, 13, 24},
	{5, 11, 14, 16},
	{7, 10, 12, 17},
	{2, 9, 15, 20},
	{4, 18, 25, 31},
	{8, 19, 22, 29}},

	{{0, 11, 18, 24},
	{1, 10, 19, 25},
	{3, 9, 17, 26},
	{5, 15, 22, 30},
	{6, 14, 21, 31},
	{2, 8, 16, 27},
	{4, 12, 23, 29},
	{7, 13, 20, 28}},

	{{0, 10, 13, 22},
	{1, 4, 15, 27},
	{3, 7, 8, 30},
	{14, 19, 23, 24},
	{11, 17, 20, 31},
	{2, 21, 25, 28},
	{5, 9, 12, 18},
	{6, 16, 26, 29}},

	{{0, 9, 23, 31},
	{1, 5, 24, 29},
	{3, 14, 18, 28},
	{8, 13, 17, 21},
	{6, 10, 20, 27},
	{2, 12, 19, 30},
	{4, 11, 22, 26},
	{7, 15, 16, 25}},

	{{0, 5, 19, 20},
	{1, 6, 9, 30},
	{3, 4, 16, 21},
	{13, 18, 23, 27},
	{10, 15, 24, 28},
	{2, 7, 11, 29},
	{14, 17, 22, 25},
	{8, 12, 26, 31}},

	{{0, 15, 17, 29},
	{1, 13, 16, 31},
	{3, 12, 22, 27},
	{18, 20, 26, 30},
	{7, 9, 21, 24},
	{2, 4, 10, 14},
	{5, 8, 23, 25},
	{6, 11, 19, 28}},

	{{0, 6, 12, 25},
	{1, 8, 14, 20},
	{3, 11, 15, 23},
	{9, 16, 22, 28},
	{10, 18, 21, 29},
	{2, 5, 13, 26},
	{4, 17, 24, 30},
	{7, 19, 27, 31}},

	{{0, 7, 14, 26},
	{1, 11, 12, 21},
	{3, 20, 25, 29},
	{5, 17, 27, 28},
	{6, 8, 15, 18},
	{2, 22, 24, 31},
	{4, 9, 13, 19},
	{10, 16, 23, 30}}};

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

  // pick 8 digits in the range 0..9
  // make sure they're unique. They're the 2 rounds we're not using
  uint8_t h0 = 0;
  uint8_t rounds_to_use[HANCHAN];
  for (uint8_t h = 0; h < 10; h++) {
    if (h != IGNORE_H1 && h != IGNORE_H2) {
      rounds_to_use[h0] = h;
      h0++;
    }
  }

  // for each round, pick TABLES numbers 0..TABLES
  // make sure they're unique. That's the table order
  uint8_t table_order[HANCHAN][TABLES] = {-1};
  for (uint8_t h = 0; h < HANCHAN; h++) {
    uint8_t used_tables[8] = {0};
    for (uint8_t t = 0; t < TABLES; t++) {
      uint8_t rnd = GUESS_UINT8_T();
      CHECK(rnd < TABLES && used_tables[rnd] == 0);
      used_tables[rnd]++;
      table_order[rounds_to_use[h]][t] = rnd;
    }
  }

  // now at each table, order the players in a random order
  for (uint8_t h = 0; h < HANCHAN; h++) {
    for (uint8_t t = 0; t < TABLES; t++) {
      uint8_t wind_order = GUESS_UINT8_T();
      CHECK(wind_order < PERMUTATIONS);
      for (uint8_t s = 0; s < SIZE; s++) {
        uint8_t seat = SEATING[wind_order][s];
        uint8_t p = initial_seats[rounds_to_use[h]][table_order[h][t]][s];
        seats[h][t][seat] = p;
        winds[p][seat]++;
        tables[p][t]++;
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

      printf("\n\n TABLE COUNT BY PLAYER\n");

      for (uint8_t p = 0; p < PLAYERS; p++) {
        for (uint8_t t = 0; t < TABLES; t++) {
          printf("%3d, ", tables[p][t]);
        }
        printf("\n");
      }

  );
  // -->
}
