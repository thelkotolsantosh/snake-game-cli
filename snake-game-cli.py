#include <ncurses.h>
#include <cstdlib>
#include <ctime>
#include <vector>
#include <utility>
#include <thread>
#include <chrono>

using namespace std;

const int WIDTH = 80;
const int HEIGHT = 24;

int main() {
    srand(time(0));
    
    // Initialize ncurses
    initscr();
    cbreak();
    noecho();
    nodelay(stdscr, TRUE);
    keypad(stdscr, TRUE);
    curs_set(0);
    
    // Initialize colors
    start_color();
    init_pair(1, COLOR_GREEN, COLOR_BLACK);
    init_pair(2, COLOR_RED, COLOR_BLACK);
    init_pair(3, COLOR_YELLOW, COLOR_BLACK);
    
    // Game variables
    vector<pair<int, int>> snake = {{WIDTH/2, HEIGHT/2}};
    pair<int, int> food = {rand() % (WIDTH-2) + 1, rand() % (HEIGHT-2) + 1};
    int direction = 1; // 1=RIGHT, 2=LEFT, 3=DOWN, 4=UP
    bool game_over = false;
    int score = 0;
    
    while (!game_over) {
        clear();
        
        // Draw border
        for (int i = 0; i < WIDTH; i++) {
            mvaddch(0, i, '#');
            mvaddch(HEIGHT-1, i, '#');
        }
        for (int i = 0; i < HEIGHT; i++) {
            mvaddch(i, 0, '#');
            mvaddch(i, WIDTH-1, '#');
        }
        
        // Draw snake
        attron(COLOR_PAIR(1));
        for (auto seg : snake) {
            mvaddch(seg.second, seg.first, 'o');
        }
        attroff(COLOR_PAIR(1));
        
        // Draw food
        attron(COLOR_PAIR(2));
        mvaddch(food.second, food.first, '*');
        attroff(COLOR_PAIR(2));
        
        // Draw score
        attron(COLOR_PAIR(3));
        mvprintw(HEIGHT, 0, "Score: %d", score);
        attroff(COLOR_PAIR(3));
        
        refresh();
        
        // Input handling
        int ch = getch();
        if (ch == KEY_RIGHT && direction != 2) direction = 1;
        if (ch == KEY_LEFT && direction != 1) direction = 2;
        if (ch == KEY_DOWN && direction != 4) direction = 3;
        if (ch == KEY_UP && direction != 3) direction = 4;
        if (ch == 'q') break;
        
        // Move snake
        int new_x = snake[0].first;
        int new_y = snake[0].second;
        
        if (direction == 1) new_x++;
        if (direction == 2) new_x--;
        if (direction == 3) new_y++;
        if (direction == 4) new_y--;
        
        // Check collision with walls
        if (new_x <= 0 || new_x >= WIDTH-1 || new_y <= 0 || new_y >= HEIGHT-1) {
            game_over = true;
        }
        
        // Check collision with itself
        for (auto seg : snake) {
            if (seg.first == new_x && seg.second == new_y) {
                game_over = true;
            }
        }
        
        // Add new head
        snake.insert(snake.begin(), {new_x, new_y});
        
        // Check food collision
        if (new_x == food.first && new_y == food.second) {
            score += 10;
            food = {rand() % (WIDTH-2) + 1, rand() % (HEIGHT-2) + 1};
        } else {
            snake.pop_back();
        }
        
        this_thread::sleep_for(chrono::milliseconds(100));
    }
    
    // Game over screen
    clear();
    attron(COLOR_PAIR(2));
    mvprintw(HEIGHT/2, WIDTH/2-5, "GAME OVER!");
    mvprintw(HEIGHT/2+2, WIDTH/2-8, "Final Score: %d", score);
    attroff(COLOR_PAIR(2));
    refresh();
    getch();
    
    endwin();
    return 0;
}
