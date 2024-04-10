#Different Solving methods
from sudoku_solver_helper_functions import *

# 1. Hidden Single
# if there is only one instance of N in house - keep only it
###################################
def hidden_single(sudoku):

    def find_only_number_in_group():
        nonlocal group
        nonlocal number
        count = 0
        removed = 0
        cell_to_clean = (-1, -1)
        for cell in group:
            for n in sudoku[cell]:
                if n == number:
                    count += 1
                    cell_to_clean = cell
        if count == 1 and cell_to_clean != (-1, -1) \
           and len(sudoku[cell_to_clean]) > 1:
            removed = len(sudoku[cell_to_clean]) - 1
            sudoku[cell_to_clean] = [number]
        return removed

    count = 0
    for number in range(1, 10):
        for group in all_houses:
            count += find_only_number_in_group()
    return count


# 2. CSP
# brute force CSP solution for each cell:
# it covers hidden and naked pairs, triples, quads
################################################
def csp_list(inp):

    perm = []

    # recurive func to get all permutations
    def append_permutations(sofar):
        nonlocal inp
        for n in inp[len(sofar)]:
            if len(sofar) == len(inp) - 1:
                perm.append(sofar + [n])
            else:
                append_permutations(sofar + [n])

    append_permutations([])

    # filter out impossibble ones
    for i in range(len(perm))[::-1]:
        if len(perm[i]) != len(set(perm[i])):
            del perm[i]

    # which values are still there?
    out = []
    for i in range(len(inp)):
        out.append([])
        for n in range(10):
            for p in perm:
                if p[i] == n and n not in out[i]:
                    out[i].append(n)
    return out


def csp(s):
    count = 0
    for group in all_houses:
        house = []
        for cell in group:
            house.append(s[cell])
        house_csp = csp_list(house)
        if house_csp != house:
            for i in range(len(group)):
                if s[group[i]] != house_csp[i]:
                    count += len(s[group[i]]) - len(house_csp[i])
                    s[group[i]] = house_csp[i]
    return count


# 3. Intersection
# includes: poiting pairs, box line reduction
#############################################
def n_from_cells(s, cells):
    numbers = []
    for cell in cells:
        numbers += s[cell]
    return list(set(numbers))


# remove number n from cells cells
def remove_n_from_cells(s, n, cells):
    count = 0
    for cell in cells:
        if n in s[cell]:
            s[cell].remove(n)
            count += 1
    return count


def intersect(s):
    count = 0
    for block in all_blocks:
        for line in all_rows + all_columns:

            # get the block/line/intersection coords
            sblock = set(block)
            sline = set(line)
            both = sblock.intersection(line)
            if len(both) == 0:
                continue  # if no intersection - go to next
            only_b = sblock.difference(both)
            only_l = sline.difference(both)

            # get the numbers from those region
            n_only_b = n_from_cells(s, only_b)
            n_both = n_from_cells(s, both)
            n_only_l = n_from_cells(s, only_l)

            # go through all numbers
            for i in range(1, 10):
                if i in n_both and i in n_only_b and i not in n_only_l:
                    count += remove_n_from_cells(s, i, list(only_b))
                if i in n_both and i not in n_only_b and i in n_only_l:
                    count += remove_n_from_cells(s, i, list(only_l))
    return count


# 4. X-Wing
# it actually is a subset of Nice-chains, but okay,
# let's keep it because it is kind of famous
##################################################
def n_from_cells_dup(s, cells):
    numbers = []
    for cell in cells:
        numbers += s[cell]
    return numbers


def x_wing(s):
    count = 0
    for h1 in range(0, 9):
        for h2 in range(h1 + 1, 9):
            for v1 in range(0, 9):
                for v2 in range(v1 + 1, 9):
                    hline1 = all_rows[h1]
                    hline2 = all_rows[h2]
                    vline1 = all_columns[v1]
                    vline2 = all_columns[v2]

                    s_rows = set(hline1).union(set(hline2))
                    s_cols = set(vline1).union(set(vline2))
                    cross_4 = s_rows.intersection(s_cols)
                    if len(cross_4) != 4:
                        continue  # wrong cross-section
                    only_row = s_rows.difference(cross_4)
                    only_col = s_cols.difference(cross_4)

                    # get the numbers from those region
                    n_cross = n_from_cells_dup(s, cross_4)
                    n_only_row = n_from_cells(s, only_row)
                    n_only_col = n_from_cells(s, only_col)

                    # go through all numbers
                    for i in range(1, 10):
                        if n_cross.count(i) == 4:
                            if i in n_only_row and i not in n_only_col:
                                count += \
                                      remove_n_from_cells(s, i, list(only_row))
                            if i not in n_only_row and i in n_only_col:
                                count += \
                                      remove_n_from_cells(s, i, list(only_col))
    # print ("X:", time.time()-t)
    return count


# 5. Coloring
##############################
def get_a_hard_link(s, n, group, add_n=False):
    links = []
    for cell in group:
        if n in s[cell]:
            links.append(cell)
    if len(links) == 2:
        if add_n:
            links.append(n)
        return links
    return []


def get_all_hard_links(s, n, add_n=False):
    hard_links = []
    for group in all_houses:
        new_link = get_a_hard_link(s, n, group, add_n)
        if new_link != [] and new_link not in hard_links:
            hard_links.append(new_link)
    return hard_links


def get_link_chains(links_original):
    links = links_original.copy()
    groups = []
    while len(links) > 0:
        has_to_add = True
        groups.append([])
        groups[-1].append(links[0])
        del (links[0])
        while has_to_add:
            has_to_add = False
            for link in groups[-1]:
                for cell in link:
                    for i in range(len(links))[::-1]:
                        if links[i][0] == cell or links[i][1] == cell:
                            groups[-1].append(links[i])
                            del (links[i])
                            has_to_add = True
    return groups


def ab_group(chain):
    a = [chain[0][0]]
    b = [chain[0][1]]
    keep_going = True
    while keep_going:
        keep_going = False
        for link in chain:
            if link[0] in a and link[1] not in b:
                b.append(link[1])
                keep_going = True
            if link[0] in b and link[1] not in a:
                a.append(link[1])
                keep_going = True
            if link[1] in a and link[0] not in b:
                b.append(link[0])
                keep_going = True
            if link[1] in b and link[0] not in a:
                a.append(link[0])
                keep_going = True
    return (a, b)


def twice_in_a_house(s, n, a):
    result = 0  # sorry for inconsistency here, count was already taken
    for house in all_houses:
        count = 0
        for cell in house:
            if cell in a and n in s[cell]:
                count += 1
        if count > 1:
            for cell in a:
                if n in s[cell]:
                    s[cell].remove(n)
                    result += 1
    return result


def two_colors_elsewhere(s, n, all_a, all_b):
    count = 0
    for (j, i) in range2(9, 9):
        spotted_a, spotted_b = False, False
        if (i, j) not in all_a and (i, j) not in all_b and n in s[i, j]:
            spotted_a, spotted_b = False, False
            for house in all_houses:
                if (i, j) in house:
                    for a in all_a:
                        if a in house:
                            spotted_a = True
                    for b in all_b:
                        if b in house:
                            spotted_b = True
        if spotted_a and spotted_b:
            s[i, j].remove(n)
            count += 1
    return count


def coloring(s):
    count = 0
    for n in range(1, 10):
        hard_links = get_all_hard_links(s, n)
        chains = get_link_chains(hard_links)
        for chain in chains:
            if len(chain) > 1:
                a, b = ab_group(chain)
                count += twice_in_a_house(s, n, a)
                count += twice_in_a_house(s, n, b)
                count += two_colors_elsewhere(s, n, a, b)
    return count


# 6. Y-Wing
#############
def y_wing(s):
    count = 0
    hard_links = []
    for n in range(1, 10):
        hard_links += get_all_hard_links(s, n, add_n=True)
    for link1 in hard_links:
        for link2 in hard_links:
            if link1[2] != link2[2] and \
                   (link1[0] == link2[0] or link1[0] == link2[1] or
                    link1[1] == link2[0] or link1[1] == link2[1]) \
                    and len(s[link1[0]]) == 2 and len(s[link1[1]]) == 2 \
                    and len(s[link2[0]]) == 2 and len(s[link2[1]]) == 2:
                for house in all_houses:
                    if link1[0] in house and link1[1] in house \
                       and link2[0] in house and link2[1] in house:
                        break
                else:
                    y_horns = []
                    for cell in link1 + link2:
                        if cell in y_horns:
                            y_horns.remove(cell)
                        else:
                            y_horns.append(cell)
                    for n in s[y_horns[0]]:
                        if n in s[y_horns[2]] \
                           and n != y_horns[1] \
                           and n != y_horns[3]:
                            count += \
                                two_colors_elsewhere(s, n,
                                                     (y_horns[0],),
                                                     (y_horns[2],))
    return count


# 7. Nice Chains
# a.k.a. X-cycles, nice loops
################################
def get_soft_links_from_group(s, n, group):
    found = []
    for cell in group:
        if n in s[cell]:
            found.append(cell)
    if len(found) < 3:
        return []

    links = []
    for cell1 in found:
        for cell2 in found:
            if cell1 != cell2 and [cell2, cell1] not in links:
                links.append([cell1, cell2])
    return links


def get_all_soft_links(s, n):
    soft_links = []
    for group in all_houses:
        new_links = get_soft_links_from_group(s, n, group)
        if new_links != []:
            soft_links += new_links
    return soft_links


def add_reverse_links(links):
    out = []
    for link in links:
        out.append(link)
        out.append([link[1], link[0]])
    return out


# chains - for out data
def find_nice_chains(link, hard_links, soft_links, chains):
    last_cell = link[-1]
    for slink in soft_links:
        if slink[0] == last_cell:
            if slink[1] == link[0]:
                chains.append(link)
            else:
                for hlink in hard_links:
                    if hlink[0] == slink[1]:
                        if len(link + [hlink[0]] + [hlink[1]]) < 20:
                            find_nice_chains(link + [hlink[0]] + [hlink[1]],
                                             hard_links, soft_links, chains)


def double_hard_links(hard_links):
    dlinks = []
    for link1 in hard_links:
        for link2 in hard_links:
            # share 1 cell
            if len(set(link1 + link2)) == 3 and link1[1] == link2[0]:
                dlinks.append([link1[0], link1[1], link2[1]])
    return dlinks


def soft_hard_links(soft_links, hard_links):
    shlinks = []
    for link1 in soft_links:
        for link2 in hard_links:
            # share 1 cell
            if len(set(link1+link2)) == 3 and link1[1] == link2[0]:
                shlinks.append([link1[0], link1[1], link2[1]])
    return shlinks


def nice_chains(s):
    count = 0
    for n in range(1, 10):
        chains = []
        hard_links = get_all_hard_links(s, n)
        hard_links2 = add_reverse_links(hard_links)
        soft_links = get_all_soft_links(s, n)
        soft_links2 = add_reverse_links(soft_links)

        # Continuous chains
        for link in hard_links:
            find_nice_chains(link, hard_links2, soft_links2, chains)
        for chain in chains:
            all_a = [chain[i] for i in range(len(chain)) if i % 2 == 0]
            all_b = [chain[i] for i in range(len(chain)) if i % 2 == 1]
            count += two_colors_elsewhere(s, n, all_a, all_b)

        # Two hard in a row
        dlinks = double_hard_links(hard_links2)
        for dlink in dlinks:
            chains = []
            find_nice_chains(dlink, hard_links2, soft_links2, chains)
            if len(chains) > 0:
                for i in range(1, 10):
                    if i != n and i in s[dlink[1]]:
                        s[dlink[1]].remove(i)
                        count += 1

        # Two soft in a row
        shlinks = soft_hard_links(soft_links2, hard_links2)
        for shlink in shlinks:
            chains = []
            find_nice_chains(shlink, hard_links2, soft_links2, chains)
            if len(chains) > 0:
                if n in s[shlink[0]]:
                    s[shlink[0]].remove(n)
                    count += 1
    return count


# 8. 3D Medusa
##############
def get_all_bicells(s):
    bicells = []
    for (i, j) in range2(9, 9):
        if len(s[i, j]) == 2:
            bicells.append([(i, j), s[i, j][0], s[i, j][1]])
    return bicells


def get_medusa_chains(links_original, bicells_original):
    links = links_original.copy()
    bicells = bicells_original.copy()
    groups = []
    while len(links):
        has_to_add = True
        groups.append([])
        groups[-1].append(links[0])
        del (links[0])
        while has_to_add:
            has_to_add = False
            for link in groups[-1]:
                if type(link[1]) == tuple:  # it's a link
                    for cell in link[0:2]:
                        # add other links
                        for i in range(len(links))[::-1]:
                            if (links[i][0] == cell or links[i][1] == cell) \
                                    and link[2] == links[i][2]:
                                groups[-1].append(links[i])
                                del (links[i])
                                has_to_add = True
                        # add other bicells
                        for i in range(len(bicells))[::-1]:
                            if bicells[i][0] == cell \
                                    and (link[2] == bicells[i][1] \
                                    or link[2] == bicells[i][2]):
                                groups[-1].append(bicells[i])
                                del (bicells[i])
                                has_to_add = True
                else:  # it's a bicell
                    # add other links
                    for i in range(len(links))[::-1]:
                        if (links[i][0] == link[0]
                                or links[i][1] == link[0]) \
                                and (links[i][2] == link[1]
                                or links[i][2] == link[2]):
                            groups[-1].append(links[i])
                            del (links[i])
                            has_to_add = True
    return groups


def cell_in_ab_medusa_chain(cell, chain, n):
    for link in chain:
        if link[0] == cell and n == link[1]:
                return True
    return False


def ab_group_medusa(chain):
    a = [(chain[0][0], chain[0][2]),]
    b = [(chain[0][1], chain[0][2]),]
    keep_going = True
    while keep_going:
        keep_going = False
        for link in chain:
            if type(link[1]) == tuple:  # it's a link
                if cell_in_ab_medusa_chain(link[0], a, link[2]) and not cell_in_ab_medusa_chain(link[1], b, link[2]):
                    b.append((link[1], link[2]))
                    keep_going = True
                if cell_in_ab_medusa_chain(link[0], b, link[2]) and not cell_in_ab_medusa_chain(link[1], a, link[2]):
                    a.append((link[1], link[2]))
                    keep_going = True
                if cell_in_ab_medusa_chain(link[1], a, link[2]) and not cell_in_ab_medusa_chain(link[0], b, link[2]):
                    b.append((link[0], link[2]))
                    keep_going = True
                if cell_in_ab_medusa_chain(link[1], b, link[2]) and not cell_in_ab_medusa_chain(link[0], a, link[2]):
                    a.append((link[0], link[2]))
                    keep_going = True
            else: # it's a bicell
                if cell_in_ab_medusa_chain(link[0], a, link[1]) and not cell_in_ab_medusa_chain(link[0], b, link[2]):
                    b.append((link[0], link[2]))
                    keep_going = True                    
                if cell_in_ab_medusa_chain(link[0], b, link[1]) and not cell_in_ab_medusa_chain(link[0], a, link[2]):
                    a.append((link[0], link[2]))
                    keep_going = True                    
                if cell_in_ab_medusa_chain(link[0], a, link[2]) and not cell_in_ab_medusa_chain(link[0], b, link[1]):
                    b.append((link[0], link[1]))
                    keep_going = True                    
                if cell_in_ab_medusa_chain(link[0], b, link[2]) and not cell_in_ab_medusa_chain(link[0], a, link[1]):
                    a.append((link[0], link[1]))
                    keep_going = True                    
    return  (a, b)

def same_color_twice_in_cell(s, a):
    count = 0 
    for cell1 in a:
        for cell2 in a:
            if cell1[0] == cell2[0] and cell1[1] != cell2[1]:
                for cell in a:
                    count += remove_n_from_cells(s, cell[1], (cell[0],))
    return count

def twice_in_a_house_medusa(s, a):
    count = 0
    for house in all_houses:
        n_count = [0] * 9
        for cell in a:
            if cell[0] in house:
                n_count[cell[1] - 1] += 1
        if n_count.count(2) > 0:
            pass
            # this one is not finished, cause I haven't found any examples in my set
    return count
        
def two_colors_in_a_cell(s, a, b):
    count = 0
    for (i, j) in range2(9, 9):
        found_colors = []
        if len(s[i,j])>2:
            for cell in a+b:
                if cell[0] == (i, j):
                    found_colors.append(cell[1])
        if len(found_colors) > 1:
            for n in s[i, j]:
                if n not in found_colors:
                    s[i, j].remove(n)
                    count += 1
    return count


def cell_in_chain(cell, chain):
    for link in chain:
        if link[0] == cell:
                return True
    return False


def two_colors_elsewhere_medusa(s, all_a, all_b):
    count = 0
    for (i, j) in range2(9, 9):
        if not cell_in_chain((i, j), all_a) and not cell_in_chain((i,j), all_b):
            for n in s[i, j]:
                spotted_a, spotted_b = False, False
                for house in all_houses:
                    if (i, j) in house:
                        for a in all_a:
                            if a[0] in house and a[1] == n:
                                spotted_a = True
                        for b in all_b:
                            if b[0] in house and b[1] == n:
                                spotted_b = True
                if spotted_a and spotted_b:
                    s[i, j].remove(n)
                    count += 1
    return count


def get_n_cell_in_chain(needle_cell, chain):
    for cell in chain:
        if cell[0] == needle_cell:
            return cell[1]
    return None


def two_colors_unit_cell(s, all_a, all_b):
    count = 0
    for (i, j) in range2(9, 9):  # go through all cells
        for (a, b) in [(all_a, all_b), (all_b, all_a)]:  # A-cell, B-house; then the other way round
            if len(s[i, j])>1 and cell_in_chain((i, j), a) and not cell_in_chain((i, j), b): # 2+ numbers in cell, from one chain, but not from the other
                in_cell = get_n_cell_in_chain((i, j), a)  # The number that is from the chain
                for n in s[(i, j)]:  # Go through the numbers in the cell
                    if n != in_cell:  # Except for the one from the chain
                        for house in all_houses:  # Look at all houses
                            if (i, j) in house:  # That the cell can see
                                for cell in house:  # and then look through house's cells
                                    if cell_in_chain(cell, b) and get_n_cell_in_chain(cell, b) == n: # Is there an item from another chain
                                        if n in s[i, j]:  # In case we've done it already
                                            s[i, j].remove(n)
                                            count += 1
    return count

def empty_by_color(s, all_a, all_b):
    count = 0
    for (i, j) in range2(9, 9):
        for (a, b) in [(all_a, all_b), (all_b, all_a)]:
            if len(s[i, j])>1 and not cell_in_chain((i, j), a) and not cell_in_chain((i, j), b):
                found = []
                for n in s[i, j]:
                    for house in all_houses:
                        if (i, j) in house:
                            for cell in house:
                                if cell_in_chain(cell, a) and get_n_cell_in_chain(cell, a) == n:
                                    found.append( get_n_cell_in_chain(cell, a) )
                if set(found) == set(s[i, j]):
                    for cell in a: 
                        if cell[1] in s[cell[0]]:
                            s[cell[0]].remove(cell[1])
                            count += 1
                    return count
    return count


def medusa_3d(s):
    count = 0
    hard_links = []
    for n in range(1, 10):
        hard_links += get_all_hard_links(s, n, add_n=True)
    bicells = get_all_bicells(s)
    chains = get_medusa_chains(hard_links, bicells)
    for chain in chains:
        if len(chain) > 1:
            a, b = ab_group_medusa(chain)
            count += same_color_twice_in_cell(s, a)
            count += same_color_twice_in_cell(s, b)
            count += twice_in_a_house_medusa(s, a)
            count += twice_in_a_house_medusa(s, b)
            count += two_colors_in_a_cell(s, a, b)
            count += two_colors_elsewhere_medusa(s, a, b)
            count += two_colors_unit_cell(s, a, b)
            count += empty_by_color(s, a, b)
    return count
