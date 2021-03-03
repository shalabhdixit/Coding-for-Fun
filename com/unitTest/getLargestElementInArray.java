package com.unitTest;

import static org.testng.Assert.assertEquals;

import org.testng.annotations.Test;

import com.sourceCode.ArrayUtil;

public class getLargestElementInArray {

	/*public static void main(String args[]) {
		int array[] = { 10, 90, 100, 3, 600, 500, 4, 90 };

		System.out.println("Largest Element in the array: " + ArrayUtil.getLargestElement(array));
	}*/

	@Test(testName = "Valid Integer Array", description = "Validate that largest element should be displayed from the valid input array", priority=0)
	public void getLargestArrayElement_ValidIntArray() {
		int arr[] = { 10, 90, 100, 3, 600, 500, 4, 90 };

		assertEquals(600, ArrayUtil.getLargestElement(arr));
	}

	@Test(testName = "Array with Negative values", description = "Validate that largest element should be displayed from the array containing negative values",priority=1)
	public void getLargestArrayElement_NegativeValuesArray() {
		int arr[] = { -10, -80, -1, -9, -3 };

		assertEquals(-1, ArrayUtil.getLargestElement(arr));
	}
}