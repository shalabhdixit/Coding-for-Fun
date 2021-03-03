/**
 * Defines set of reusable functions for an array
 * Function-1: getLength - It will give total number of items of an array
 * Function-2: getLargestElement - It will give largest element in an array of integers
 */

package com.sourceCode;

public class ArrayUtil {

	/**
	 * Function to count total number of items in an array
	 * 
	 * @param array
	 *            - Takes array parameter of Integer type
	 * @return - number of items in the array
	 */
	public static int getLength(int[] array) {
		int arrLength = 0;

		for (int i : array) {
			arrLength++;
		}
		return arrLength;
	}

	/**
	 * Function to find the largest element in an integer array
	 * 
	 * @param array
	 *            - Takes array parameter of Integer type
	 * @return - Largest element in the array
	 */
	public static int getLargestElement(int[] array) {
		int largestElement = array[0];

		for (int arrIdx = 1; arrIdx < getLength(array); arrIdx++) {

			if (array[arrIdx] > largestElement) {
				largestElement = array[arrIdx];
			}
		}
		return largestElement;
	}
}