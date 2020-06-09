import gemmi


def update_star(starfile, ice_groups):
    in_doc = gemmi.cif.read_file(starfile)
    block = in_doc.find_block('particles')
    new_document = gemmi.cif.Document()
    block_one = new_document.add_new_block('particles')
    for x in block:
        table = x.loop

    tags = table.tags
    table = block.find(tags)

    tags.append('_ibIceGroup')  # add new tag:
    loop = block_one.init_loop('', tags)  # make temp new table
    for i in range(len(table)):
        row = table[i]
        new_row = list(row)
        print(new_row)
        new_row.append(f'{ice_groups[i]}')
        loop.add_row(new_row)  # update temp new table with all data

    # new_table = block_one.find(tags)
    # new_loop = block.init_loop('_test', tags)  # replace original table with new
    # for row in new_table:
    #     new_loop.add_row(new_row)

    new_document.write_file('particles.star')


if __name__ == '__main__':
    starfile = '/home/lexi/Documents/Diamond/ICEBREAKER/test_data/particles.star'
    update_star(starfile)
