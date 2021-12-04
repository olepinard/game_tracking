import os
import sys
import pandas as pd
import argparse


def main(name):
    parser = argparse.ArgumentParser(description='Keep track of a boardgame leaderboard.')
    parser.add_argument('--game', type=str, nargs='+',
                        help='What game did you play: azul, azul_dual, tarot (coming soon), '
                             ' elevator (coming soon), dominion (coming soon)')
    parser.add_argument('--players', type=str, nargs='+',
                        help='who played and what was their score exp. "Octave 102" ')

    args = parser.parse_args()

    num = len(args.players)
    if (num % 2) != 0:
        print("The list of players and score was incorrectly entered")
        exit()

    ranks = pd.read_csv("total.csv")

    if args.game[0] == 'azul':
        azul(args.players, ranks)

    if args.game[0] == 'azul_dual':
        if num == 4:
            azul_two(args.players, ranks)
        else:
            print("azul_dual is for two players only")


def update_csv(game, game_ranks, ranks, game_name):
    for i in range(len(game["name"])):
        if len(game_ranks[game_ranks["name"] == game["name"][i]]) == 0:
            question = input("Do you want to make a new entry for " + game["name"][i] + " [y/n]")
            if question == "y":
                game_ranks = game_ranks.append(
                    {'name': game["name"][i], 'rank': game["rank"][i], 'change': int(game["dif"][i])},
                    ignore_index=True)
            else:
                print("Please re-enter the scores")
                exit()
        else:
            game_ranks = game_ranks.loc[game_ranks["name"] != game["name"][i]]
            game_ranks = game_ranks.append(
                {'name': game["name"][i], 'rank': game["rank"][i], 'change': int(game["dif"][i])}, ignore_index=True)

        if len(ranks[ranks["name"] == game["name"][i]]) == 0:
            question = input("Do you want to make a new entry for " + game["name"][i] + " in totals? [y/n]")
            if question == "y":
                ranks = ranks.append(
                    {'name': game["name"][i], 'total rank': game["trank"][i], 'total change': int(game["tdif"][i])},
                    ignore_index=True)
            else:
                print("Please re-enter the scores")
                exit()
        else:
            ranks = ranks.loc[ranks["name"] != game["name"][i]]
            ranks = ranks.append(
                {'name': game["name"][i], 'total rank': game["trank"][i], 'total change': int(game["tdif"][i])},
                ignore_index=True)

    ranks.to_csv("total.csv", index=False)
    game_ranks.to_csv(game_name + ".csv", index=False)

    print_game = pd.merge(left=game_ranks, right=ranks, left_on='name', right_on='name')
    print_game = print_game.sort_values(by=['rank'], ascending=False)
    print_game = print_game.reset_index(drop=True)
    print_game.index += 1
    print(print_game)


def azul(players, ranks):
    azul_ranks = pd.read_csv("azul.csv")
    number_of_players = int(len(players) / 2)

    game = get_player_standings(players, ranks, azul_ranks, number_of_players)

    game = get_escore(game, number_of_players)
    game = azul_rank(game, number_of_players)

    update_csv(game, azul_ranks, ranks, "azul")

    return


def azul_two(players, ranks):
    azul_ranks = pd.read_csv("azul_dual.csv")
    number_of_players = int(len(players) / 2)

    game = get_player_standings(players, ranks, azul_ranks, number_of_players)

    game = get_escore(game, number_of_players)
    game = azul2_rank(game, number_of_players)

    update_csv(game, azul_ranks, ranks, "azul_dual")

def get_player_standings(players, ranks, game_ranks, num):
    game = {
        "name": [],
        "rank": [],
        "trank": [],
        "score": [],
        "escore": [],
        "tescore": [],
        "dif": [],
        "tdif": []
    }
    for i in range(num):
        game["name"].append(players[i * 2])
        game["score"].append(int(players[i * 2 + 1]))
        game["rank"].append(get_score(game["name"][i], game_ranks))
        game["trank"].append(get_score(game["name"][i], ranks))

    return game


def azul2_rank(game, num):
    coefficient = 1/(min(game["score"])/max(game["score"]) )**4
    maxim = max(game["score"]) - min(game["score"])
    print(coefficient)
    if coefficient > 3:
        coefficient = 3


    for i in range(num):
        norm = (game["score"][i] - min(game["score"])) / maxim
        game["rank"][i] = int(game["rank"][i] + 15 * (norm - game["escore"][i])*coefficient)
        game["dif"].append(15 * (norm - game["escore"][i])*coefficient)
        game["trank"][i] = int(game["trank"][i] + 15 * (norm - game["tescore"][i])*coefficient)
        game["tdif"].append(15 * (norm - game["tescore"][i])*coefficient)

    print(game)

    return game



def azul_rank(game, num):
    maxim = max(game["score"]) - min(game["score"])
    for i in range(num):
        norm = (game["score"][i] - min(game["score"])) / maxim
        game["rank"][i] = int(game["rank"][i] + 40 * (norm - game["escore"][i]))
        game["dif"].append(40 * (norm - game["escore"][i]))
        game["trank"][i] = int(game["trank"][i] + 40 * (norm - game["tescore"][i]))
        game["tdif"].append(40 * (norm - game["tescore"][i]))
    return game


def get_escore(game, num):
    for i in range(num):
        rank = game["rank"][i]
        trank = game["trank"][i]

        avg_opponent = 0
        for t in range(len(game["name"])):
            if t != i:
                avg_opponent += game["rank"][t]
        avg_rank = avg_opponent / (len(game["name"]) - 1)

        tavg_opponent = 0
        for t in range(len(game["name"])):
            if t != i:
                tavg_opponent += game["trank"][t]
        avg_trank = tavg_opponent / (len(game["name"]) - 1)

        game["escore"].append(1 / (1 + 10 ** ((avg_rank - float(rank)) / 400)))
        game["tescore"].append(1 / (1 + 10 ** ((avg_trank - float(trank)) / 400)))
    return game


def get_score(name, csv):
    if len(csv[csv["name"] == name]) == 0:
        return 1500

    else:
        return csv[csv["name"] == name].to_numpy()[0][1]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main(sys.argv[1:])

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
