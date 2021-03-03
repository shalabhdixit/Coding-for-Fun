package com.sourceCode;

public class Tree {

	public void inorderTraveral(Node root) {
		if (root == null)
			return;
		else {
			inorderTraveral(root.leftChild);
			System.out.println(root.key);
			inorderTraveral(root.rightChild);
		}
	}
}