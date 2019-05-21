import pandas as pd
import cv2 
import os
import matplotlib.pyplot as plt
import csv

from pprint import pprint

vid_home = '/home/austin/datasets/MARE/raw'
frame_home = '/home/austin/datasets/MARE/frames'

lid_to_offset = {'517_1160': -1851045, '520_1140': -2007187, '524_1170': -1615301, '532_620': -46680}

def extract_frames(lid, frames):
    video_path = os.path.join(vid_home, str(lid) + '.VOB')
    dest = os.path.join(frame_home, str(lid))
    if not os.path.isdir(dest):
        os.mkdir(dest)
    else:
        print('warning: {} already exists'.format(dest))

    # Opens the Video file
    cap= cv2.VideoCapture(video_path)
    i=0 
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        if i in frames:
            print('{}_{}.png'.format(lid, i))
            cv2.imwrite( os.path.join(dest, '{}_{}.png'.format(lid, i)), frame)
        i+=1

    cap.release()
    cv2.destroyAllWindows()

def get_frame_num(lid, tc):
    # this will fail if we go to next day or something
    FPS = 30

    offset = lid_to_offset[lid]
    hour = tc.hour
    minute = tc.minute
    second = tc.second
    seconds = 3600*hour + 60*minute + second

    return (seconds*FPS + offset)

def plot_stats(dfs):
    for df_key in ['Fish', 'Inverts']:
        if df_key == 'pass':
            continue
        print(df_key)
        per_class_counts = {}
        df = dfs[df_key]
        spec_set = set()
        for i in range(len(df['CommonName'])):
            cn = df['CommonName'][i]
            if cn in spec_set:
                per_class_counts[cn] += 1
            else:
                per_class_counts[cn] = 1
                spec_set.add(df['CommonName'][i])

        print(len(spec_set))
        pprint(per_class_counts)

        xs = []
        ys = []
        for k,v in per_class_counts.items():
            xs.append(k[:9])
            ys.append(v)

        # plt.hist(ys)
        # plt.scatter(xs, ys)
        plt.bar(xs, ys)
        plt.show()

def organize_dfs(dfs):
    lineID_2_f2IDs = {}
    # for df_key in dfs.keys():
    IDs = set()
    for df_key in ['Fish', 'Inverts']:
        # are IDs unique across sheets..? IDs makes sure they are
        if df_key == 'Habitat':
            pass

        df = dfs[df_key]
        for i in range(len(df)):
            lineID = df['LineID'][i]
            frame_num = get_frame_num(lineID, df['TC'][i])

            if lineID not in lineID_2_f2IDs.keys():
                lineID_2_f2IDs[lineID] = {}

            frame_to_IDs = lineID_2_f2IDs[lineID]
            assert(df['ID'][i] not in IDs)
            IDs.add(df['ID'][i])

            if frame_num not in frame_to_IDs.keys():
                frame_to_IDs[frame_num] = [ (df_key, i, df['ID'][i]) ]
            else:
                frame_to_IDs[frame_num].append( (df_key, i, df['ID'][i]) )
    return lineID_2_f2IDs
 

def generate_rows(NCOLS, dfs, lineID_2_f2IDs):
    header_row = ['filename', 'frame_number', 'survey_date', 'line_id', 'species_1', 
            'species_1_count', 'species_2', 'species_2_count', 'species_3', 'species_3_count']
    rows = []
    rows.append(header_row)
    for lineID in lineID_2_f2IDs.keys():
        frame_to_IDs = lineID_2_f2IDs[lineID]
        for frame, IDs in frame_to_IDs.items():
            row = []
            species = [None]*NCOLS
            counts = [None]*NCOLS
            fname = '{}_{}.png'.format(lineID, frame)
            for i, id_tup in enumerate(IDs):
                df_key, df_ind, anno_id = id_tup
                df = dfs[df_key]
                survey_date = df['SurveyDate'][df_ind]
                species[i] = df['CommonName'][df_ind]
                counts[i] = df['Count'][df_ind]
            row.append(fname)
            row.append(frame)
            row.append(survey_date)
            row.append(lineID)
            for i in range(NCOLS):
                row.append(species[i])
                row.append(counts[i])
            rows.append(row)
    return rows

if __name__ == "__main__":

    xlsx_name = '../raw/Fish_Invert_Habitat_Data.xlsx'
    dfs = pd.read_excel(xlsx_name, sheet_name=None)

    # plot_stats(dfs)

    # map each lineID to a dict that maps frame to (idx, ID) of whats n the frame
    lineID_2_f2IDs = organize_dfs(dfs)

    # for each video, list frames, and extract them
    for lid in lineID_2_f2IDs.keys():
        frame_to_IDs = lineID_2_f2IDs[lid]
        frames = list(frame_to_IDs.keys())
        # extract_frames(lid, frames)

    # count number of annos in each frame, and find max
    frame_2_count = {}
    counts = []
    for lineID in lineID_2_f2IDs.keys():
        f2IDs = lineID_2_f2IDs[lineID]
        for frame in f2IDs.keys():
            frame_2_count[frame] = len(f2IDs[frame])
            counts.append(len(f2IDs[frame]))
    ncols = max(counts)

    rows = generate_rows(ncols, dfs, lineID_2_f2IDs)
    print(len(rows))

    # write rows to our csv file
    with open('MARE.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

            
