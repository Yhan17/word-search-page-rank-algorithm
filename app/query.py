from app.function_utils import *
import nltk

nltk.download('rslp')
#func OK
def search(query):
    rows, word_ids = search_multiple_words(query)
    
    #Existem diferentes métodos de classificação, descomente a linha do que achar melhor
    #scores = text_link_score(rows, word_ids)
    scores = page_rank_score(rows)
    #scores = count_link_score(rows)
    #scores = score_frequence(rows)
    #scores = localization_score(rows)
    #scores = distance_score(rows)
    
    scoresorted = sorted([(score, url) for (url,score) in scores.items()], reverse=1)
    for(score, idurl) in scoresorted:
        print('%f\t%s' % (score, get_url(idurl)))

#func OK
def get_word_id(word):
    func_return = -1
    stemmer = nltk.stem.RSLPStemmer()
    cursor = connection.cursor()
    cursor.execute(f'select idpalavra from palavras where palavra="{stemmer.stem(word)}"')
    if(cursor.rowcount > 0):
        func_return = cursor.fetchone()[0]
        
    cursor.close()
    return func_return

#func OK
def search_word(word):
    word_id = get_word_id(word)
    cursor = connection.cursor()
    cursor.execute(f'select urls.url from palavra_localizacao plc inner join urls on plc.idurl = urls.idurl where plc.idpalavra={word_id}')
    pages = set()
    for url in cursor:
        pages.add(url[0])
    print(str(len(pages)))
    cursor.close()

#func OK
def search_multiple_words(query):
    field_list = 'p1.idurl'
    table_list = ''
    clausule_list = ''
    word_ids = []
    
    words = query.split(' ')
    table_number = 1
    
    for word in words:
        word_id = get_word_id(word)
        if word_id > 0:
            word_ids.append(word_id)
            if table_number > 1:
                table_list += ', '
                clausule_list += ' and '
                clausule_list += 'p%d.idurl = p%d.idurl and ' % (table_number -1, table_number  )
            field_list += ', p%d.localizacao' % table_number
            table_list += ' palavra_localizacao p%d' % table_number
            clausule_list += 'p%d.idpalavra = %d' % (table_number, word_id)
            table_number += 1
    complete_query = 'select %s from %s where %s' % (field_list, table_list, clausule_list)
    
    cursor = connection.cursor()
    cursor.execute(complete_query)
    rows = [row for row in cursor]
    cursor.close()
    return rows, word_ids

#func OK
def get_url(idurl):
    func_return = ''
    cursor = connection.cursor()
    cursor.execute(f'select url from urls where idurl={idurl}')
    if cursor.rowcount >0:
        func_return = cursor.fetchone()[0]
    
    cursor.close()
    return func_return


        
#func OK
def count_link_score(rows):
    counter = dict([row[0], 1.0] for row in rows)
    cursor = connection.cursor()
    for i in counter:
     #print(i)
     cursor.execute('select count(*) from url_ligacao where idurl_destino = %s', i)
     counter[i] = cursor.fetchone()[0]
 
    cursor.close()
    return max_normalizer(counter)
    
#func OK
def page_rank_score(rows):
    page_ranks = dict([row[0], 1.0] for row in rows)
    cursor = connection.cursor()
    for i in page_ranks:
        cursor.execute('select nota from page_rank where idurl = %s', i)
        if cursor.rowcount > 0:
            page_ranks[i] = cursor.fetchone()[0]
    cursor.close()
    return max_normalizer(page_ranks)

#func OK
def text_link_score(rows, word_ids):
    counter = dict([row[0], 0] for row in rows)
    for word_id in word_ids:
        cursor = connection.cursor()
        cursor.execute('select ul.idurl_origem, ul.idurl_destino from url_palavra up inner join url_ligacao ul on ul.idurl_ligacao = up.idurl_ligacao and up.idpalavra = %s', word_id)
        for (origin_url_id, target_url_id) in cursor:
            if target_url_id in counter:
                rank_cursor = connection.cursor()
                rank_cursor.execute('select nota from page_rank where idurl = %s', origin_url_id)
                pr = rank_cursor.fetchone()[0]
                counter[target_url_id] += pr
                rank_cursor.close()
    cursor.close()
    return max_normalizer(counter)

#func OK     
def score_frequence(rows):
  counter = dict([(row[0], 0) for row in rows])
  for row in rows:
      #print(linha)
      counter[row[0]] += 1
  return max_normalizer(counter)


#func OK     
def localization_score(rows):
    localizations = dict([row[0], 1000000] for row in rows)
    for row in rows:
        #print(linha)
        soma = sum(row[1:])
        if soma < localizations[row[0]]:
            localizations[row[0]] = soma
    return min_normalizer(localizations)

#func OK  
def min_normalizer(notas):
    menor = 0.00001
    minimo = min(notas.values())
    return dict([(id, float(minimo) / max(menor, nota)) for (id, nota) in notas.items()])

#func OK  
def max_normalizer(notas):
    menor = 0.00001
    maximo = max(notas.values())
    if maximo == 0:
        maximo = menor
    return dict([(id, float(nota) / maximo) for (id, nota) in notas.items()])

#func OK     
def distance_score(rows):
    if len(rows[0]) <= 2:
        return dict([(row[0], 1.0) for row in rows])
    distances = dict([(row[0], 1000000) for row in rows])
    for row in rows:
        dist = sum([abs(row[i] - row[i - 1]) for i in range(2, len(row))])
        if dist < distances[row[0]]:
            distances[row[0]] = dist
    return min_normalizer(distances)


#search_word('python')
#rows, word_ids = search_multiple_words('python program')

#func OK  
def calculate_page_rank(iterations):
    clear_table_cursor = connection.cursor()
    clear_table_cursor.execute('delete from page_rank')
    clear_table_cursor.execute('insert into page_rank select idurl, 1.0 from urls')
    for i in range(iterations):
        print("Iteração " + str(i + 1))
        url_cursor = connection.cursor()
        url_cursor.execute('select idurl from urls')
        for url in url_cursor:
            #print(url[0])
            pr = 0.15
            
            link_cursor = connection.cursor()
            link_cursor.execute('select distinct(idurl_origem) from url_ligacao where idurl_destino = %s', url[0])
            for link in link_cursor:
                page_rank_cursor = connection.cursor()
                page_rank_cursor.execute('select nota from page_rank where idurl = %s', link[0])
                link_page_rank = page_rank_cursor.fetchone()[0]
                cursor_count = connection.cursor()
                cursor_count.execute('select count(*) from url_ligacao where idurl_origem = %s', link[0])
                link_count = cursor_count.fetchone()[0]
                pr += 0.85 * (link_page_rank / link_count)
            update_cursor = connection.cursor()
            update_cursor.execute('update page_rank set nota = %s where idurl = %s', (pr, url[0]))
            
    update_cursor.close()
    cursor_count.close()    
    page_rank_cursor.close()
    url_cursor.close()
    link_cursor.close()
    clear_table_cursor.close()

def weights_search(query, payload: Payload):
    rows, word_ids = search_multiple_words(query)
    
    total_scores = dict([row[0], 0] for row in rows)
    
    weights = [(payload.frequence_weight, score_frequence(rows)),
               (payload.localization_weight, localization_score(rows)),
               (payload.distance_weight, distance_score(rows)),
               (payload.count_weight, count_link_score(rows)),
               (payload.page_rank_weight, page_rank_score(rows)),
               (payload.text_link_weight, text_link_score(rows, word_ids)),
               ]
    for (weight, scores) in weights:
        #print(peso)
        #print(scores)
        for url in total_scores:
            #print(url)
            total_scores[url] += weight * scores[url]
            
    ordered_score = sorted([(score, url) for (url, score) in total_scores.items()], reverse = 1)
    weighted_urls= []
    for (score, idurl) in ordered_score[0:20]:
        weighted_urls.append({
          'weight':score, 
          'url': get_url(idurl)
        })
        print('%f\t%s' % (score, get_url(idurl)))
    
    return {
      'words': query,
      'data': weighted_urls
      }
    
