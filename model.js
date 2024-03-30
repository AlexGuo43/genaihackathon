const tf = require('@tensorflow/tfjs');

// House square footage.
const data = [800, 850, 900, 950, 980, 1000, 1050, 1075, 1100, 1150, 1200, 1250, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000];

// Estimated dollar cost of house for each piece of data above (1000x square footage).
const answers = [800000, 850000, 900000, 950000, 980000, 1000000, 1050000, 1075000, 1100000, 1150000, 1200000, 1250000, 1300000, 1400000, 1500000, 1600000, 1700000, 1800000, 1900000, 2000000];

// Testing data separate from training data.
const dataTest = [886, 1225, 500];
const answersTest = [886000, 1225000, 500000];

// Create Tensor representations of our vanilla JS arrays above 
// so they can be used to train our model.
const trainTensors = {
  data: tf.tensor2d(data, [data.length, 1]),
  answer: tf.tensor2d(answers, [answers.length, 1])
};

const testTensors = {
  data: tf.tensor2d(dataTest, [dataTest.length, 1]),
  answer: tf.tensor2d(answersTest, [answersTest.length, 1])
};

// Now actually create and define model architecture.
const model = tf.sequential();

// We will use one dense layer with 1 neuron and an input of 
// a single value.
model.add(tf.layers.dense({ inputShape: [1], units: 1 }));

// Choose a learning rate that is suitable for the data we are using.
const LEARNING_RATE = 0.0001;

train();

async function train() {
  // Compile the model with the defined learning rate and specify
  // our loss function to use.
  model.compile({
    optimizer: tf.train.sgd(LEARNING_RATE),
    loss: 'meanAbsoluteError'
  });

  // Finally do the training itself over 500 iterations of the data.
  // As we have so little training data we use batch size of 1.
  // We also set for the data to be shuffled each time we try 
  // and learn from it.
  let results = await model.fit(trainTensors.data, trainTensors.answer, { epochs: 500, batchSize: 1, shuffle: true });

  // Once trained we can evaluate the model.
  evaluate();
}

async function evaluate() {
  // Predict answer for a single piece of data.
  const prediction = model.predict(tf.tensor2d([[768]]));
  prediction.print();

  // Save the model locally.
  await model.save('file://path/to/save/my-model');
}
