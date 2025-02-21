#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Copyright: Copyright (c) 2018

# All rights reserved

# Created on 2018-12-18  

# Author:Wendong Bi

# Filename: dnn.py

import tensorflow as tf
import numpy as np
import csv
import math
import time

# The variable merge function:
def variable_summaries(var):
    with tf.name_scope('summary'):
        mean = tf.reduce_mean(var)
        tf.summary.scalar('mean', mean)
        with tf.name_scope('stddev'):
            stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
        tf.summary.scalar('stddev', stddev)
        tf.summary.scalar('max', tf.reduce_max(var))
        tf.summary.scalar('min', tf.reduce_min(var))
        tf.summary.histogram('histogram', var)

def setList(index, labelNum):
    l = []
    for i in range (labelNum):
        if i == index:
            l.append(1)
        else:
            l.append(-1)
    return l

def findIndex(list, element):
    for i in list:
        if element == i:
            return list.index(i)
    return -1
#把前面10%的数据放到最后面去
def roundRobin(l, turn):
    for i in range(int(len(l)/turn)):
        l.append(l[i])
        del l[i]

def roundFunc(l, turn):
    #tmp = l
    for i in range(int(len(l)/turn)):
        l.append(l[i])
        #del tmp[i]
        del l[i]

# weight variable
def weight_variable(shape, num, stddev=0.1):
    initial = tf.truncated_normal(shape, stddev=stddev)#/math.sqrt(num)
    return tf.Variable(initial)

# biase variable
def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def layer(x, W, b, in_size, out_size, do_relu=True, do_norm=True):
    # t = tf.shape(W)
    # in_size = t[0]
    # out_size = t[1]
    with tf.name_scope('Wx'):
        kernel = tf.matmul(x, W)
        tf.summary.histogram('pre_activations', kernel)
    if do_relu:
        output = tf.nn.relu(tf.add(kernel, b))
    else:
        output = tf.add(kernel, b)

    if do_norm:
       # Batch Normalize
            fc_mean, fc_var = tf.nn.moments(
                output,
                axes=[0],   # the dimension you wanna normalize, here [0] for batch
                            # for image, you wanna do [0, 1, 2] for [batch, height, width] but not channel
            )
            scale = tf.Variable(tf.ones([out_size]))
            shift = tf.Variable(tf.zeros([out_size]))
            epsilon = 0.001

            # apply moving average for mean and var when train on batch
            ema = tf.train.ExponentialMovingAverage(decay=0.5)
            def mean_var_with_update():
                ema_apply_op = ema.apply([fc_mean, fc_var])
                with tf.control_dependencies([ema_apply_op]):
                    return tf.identity(fc_mean), tf.identity(fc_var)
            mean, var = mean_var_with_update()

            output = tf.nn.batch_normalization(output, mean, var, shift, scale, epsilon)
    tf.summary.histogram('norm', output)
    return output
if __name__ == '__main__':

    # Be verbose?
    verbose = 1

    # Get the C param of SVM
    loss_weight = 0.9

    BATCH_SIZE = 100  # The number of training examples to use per training step.

    labelList = []
    labelNum = 79
    numTrain = 5896
    numTest = 5896
    iteration = 100
    robin = 10
    batch = 100
    rate = 0.05
    errorTrain = 0
    errorTest = 0
    trX = []    # Nonex112
    trY = []    # Nonex79
    teX = []
    teY = []
    normal_cnt = 0
    disease_cnt = 0
    invalid_cnt = 0
    num=0
    #train
    fy = open('F:/ai_data/Gene_Chip_Data/E-TABM-185.sdrf.txt','r')
    fx = open('../../data_dimRed_0.9.txt','r')
    fo = open('test_output1.txt','w')
    fy.readline()
    errorTrain = 0
    suit_label = []
    finallist = []
    with open('../labelDetail/8_Characteristics [DiseaseState].csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if int(row[1]) < 10:
                suit_label.append(row[0])

    #print(suit_label)

    for i in range(0, 5896):
        line_x = fx.readline().split('\t')[:-1]
        line_x = list(map(float, line_x))
        # if(i%300 == 0):
        #   print(len(line_x))
        line_y = fy.readline().split('\t')[28:29][0].strip('"')
        if line_y in suit_label:
            continue
        else:
            if line_y[0:2] == "  ":
                invalid_cnt = invalid_cnt + 1
                continue
            else:
                if line_y == 'healthy' or line_y == 'normal':
                    normal_cnt = normal_cnt + 1
                else:
                    disease_cnt = disease_cnt + 1
                ret = findIndex(labelList, line_y)
                if ret == -1:
                    num += 1
                    labelList.append(line_y)
                    line_y = setList(len(labelList) - 1, labelNum)
                else:
                    line_y = setList(ret, labelNum)

            trX.append(line_x)
            trY.append(line_y)

    order = np.random.permutation(len(trX))
    order = order.tolist()
    tpx = [trX[i] for i in order]
    tpy = [trY[i] for i in order]
    trX = tpx
    trY = tpy
    print("num of labels:", num)

        #if(i%300 == 0):
           #print(line_y)

    #for i in range(0,590):
    #   line_x = fx.readline().split('\t')[:-1]
    #   line_x = list(map(float,line_x))
    #   teX.append(line_x)
    #    line_y = fy.readline().split('\t')[1:2][0]
    #    if line_y == 'organism_part':
    #        line_y = [1,0]
    #    else :
    #        line_y = [0,1]
    #    teY.append(line_y)

    dtlist = []
    for i in range(iteration):
        dtlist.append(0)

    for turn in range(1):
        teX = trX[0:round(len(trX) / robin)]
        teY = trY[0:round(len(trY) / robin)]
        roundRobin(trX, robin)
        roundRobin(trY, robin)
        tmpX = trX[0:len(trX)-round(len(trX) / robin)]
        tmpY = trY[0:len(trY)-round(len(trY) / robin)]
        # print(normal_cnt)
        # print(disease_cnt)
        # print(invalid_cnt)
        if turn == 0:
            print("data_size", len(trX))
            print("train_sample_size:", len(tmpX))
            print("train_label_size:", len(tmpY))
            print("dim", len(tmpX[0]))
        fx.close()
        fy.close()
        # input placeholder
        with tf.name_scope('input'):
            x = tf.placeholder(tf.float32, [None, len(tmpX[0])])  # create symbolic variables
            y_ = tf.placeholder(tf.float32, [None, labelNum])
        with tf.name_scope('dropout'):
            keep_prob = tf.placeholder(tf.float32)
         # the classification.
        # layer 1
        W1 = weight_variable(shape=[len(tmpX[0]), 256], num=len(trX[0]), stddev=0.1)
        b1 = bias_variable([256])
        l1_org = layer(x, W1, b1, len(trX[0]), 256)
        #l1_drop = tf.nn.dropout(l1_org, keep_prob)

        #layer 2
        W2 = weight_variable(shape=[256, 512], num=256,  stddev=0.1)
        b2 = bias_variable([512])
        l2_org = layer(l1_org, W2, b2, 256, 512)
        l2_drop = tf.nn.dropout(l2_org, keep_prob)

        # layer test
        W3 = weight_variable(shape=[512, 512], num=512,  stddev=0.1)
        b3 = bias_variable([512])
        l3_org = layer(l2_drop, W3, b3, 512, 512)
        l3_drop = tf.nn.dropout(l3_org, keep_prob)


        # layer 3
        W4 = weight_variable([512, 256], num=512, stddev=0.1)
        b4 = bias_variable([256])
        l4_org = layer(l3_drop, W4, b4, 512, 256)
        l4_drop = tf.nn.dropout(l4_org, keep_prob)

        #output
        W5 = weight_variable([256, labelNum], num=labelNum, stddev=0.1)
        b5 = bias_variable([labelNum])
        y_output = layer(l4_drop, W5, b5, 256, labelNum, do_norm=False, do_relu=False)
      

        # # test
        # # layer 1
        # W1 = weight_variable(shape=[len(trX[0]), labelNum], num=len(trX[0]), stddev=0.1)
        # b1 = tf.Variable(tf.zeros([labelNum]))
        # y_output = tf.matmul(x,W1) + b1
        # y_output = layer(x, W1, b1, len(trX[0]), labelNum, do_relu=False, do_norm=False)
        # y_output = tf.nn.dropout(l1_org, keep_prob)

        # Optimization.
        with tf.name_scope('loss'):
            with tf.name_scope('regularization_loss'):
                regularization_loss = (1-loss_weight) * tf.reduce_sum(tf.square(W1))
            # layer_loss = tf.reduce_mean(-tf.reduce_sum(y*tf.log(y_output),reduction_indices=[1]))
            # layer_loss = tf.reduce_sum(tf.maximum(tf.zeros([batch, labelNum]), 1 - y * y_output));
            with tf.name_scope('cross_entropy'):
                layer_loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=y_output, labels=y_))
            with tf.name_scope('Total_loss'):
                loss = regularization_loss + loss_weight * layer_loss
        with tf.name_scope('train'):
            train_step = tf.train.AdamOptimizer(1e-4).minimize(loss)

        # Evaluation.
        with tf.name_scope('accuracy'):
            predicted_class = tf.sign(y_output);
            with tf.name_scope('correct_prediction'):
                correct_prediction = tf.equal(y_, predicted_class)
            with tf.name_scope('accuracy'):
                accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))-0.05
            tf.summary.scalar('accuracy', accuracy)
        aclist = []

        saver = tf.train.Saver()
        
        log_dir = 'logs'
        # Launch the graph in a session
        initial_time = time.time()
        with tf.Session() as sess:
                #with tf.device("/gpu:0"):
                # you need to initialize all variables
                tf.global_variables_initializer().run()
                merged = tf.summary.merge_all()
                train_writer = tf.summary.FileWriter(log_dir + '/train', sess.graph)
                test_writer = tf.summary.FileWriter(log_dir + '/test')
                for i in range(iteration):
                    for start, end in zip(range(int(len(tmpX) / robin), len(tmpX), batch),
                                          range(int(len(tmpX) / robin) + batch, len(tmpX) + 1, batch)):
                        sess.run(train_step, feed_dict={x: tmpX[start:end], y_: tmpY[start:end], keep_prob:0.5})
                        summary = sess.run(merged, feed_dict={x: tmpX[start:end], y_: tmpY[start:end], keep_prob:0.5})
                        train_writer.add_summary(summary, i)
                    # if iteration%10 == 0:
                    #         print("train_loss", loss.eval(feed_dict={x: tmpX[start:end], y: tmpY[start:end], keep_prob:1}))
                    
                    if i%10 == 0:
                        summary = sess.run(merged, feed_dict={x: teX, y_: teY, keep_prob:1})
                        accu = accuracy.eval(feed_dict={x: teX, y_: teY, keep_prob:1})
                        test_writer.add_summary(summary, i)
                        aclist.append(accu)
                        dtlist[i] += accu
                        print('Epoch:%d -------------- Step_Accuracy: %f' % (i, accu))
                finallist.append(sum(aclist) / len(aclist))
                saver.save(sess, log_dir + '/model.ckpt', i)
                #print(dtlist[i])
                print('Result:%d -------------- Final_avaccuracy: %f .' % (turn+1, accu))
                train_writer.close()
                test_writer.close()
    end_time = time.time()
    durationg = end_time - initial_time
    print("Everage_avaccuracy:", sum(finallist) / len(finallist))
    print("Training_time:", durationg)
    dtlist = [item / 10.0 for item in dtlist]
    for item in dtlist:
        fo.write(str(item) + '\n')
    fo.close()

