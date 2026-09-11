function divide(arr) {
  let lhs = arr.slice(0, arr.length / 2);
  let rhs = arr.slice(arr.length / 2);

  return [lhs, rhs];
}

function conquer(lhs, rhs) {
  let leftPointer = 0;
  let rightPointer = 0;
  const result = [];

  while (leftPointer <= lhs.length - 1 || rightPointer <= rhs.length - 1) {
    const leftItem = lhs[leftPointer];
    const rightItem = rhs[rightPointer];

    if (leftItem == undefined || leftItem > rightItem) {
      result.push(rightItem);
      rightPointer++;
    } else {
      result.push(leftItem);
      leftPointer++;
    }
  }

  return result;
}

let merge = false;

function mergeSort(arr) {
  if (arr.length === 1) {
    return arr;
  }

  const [lhs, rhs] = divide(arr);
  const sortedLhs = mergeSort(lhs);
  const sortedRhs = mergeSort(rhs);

  return conquer(sortedLhs, sortedRhs);
}

const arr = [];

for (let i = 0; i < 100; i++) {
  const rand = Math.floor(Math.random() * 100);
  arr.push(rand);
}

console.log(arr);

const sorted = mergeSort(arr);
console.log(sorted);
