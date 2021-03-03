package com.sourceCode;

public class Node {
	public Node leftChild;
	public Node rightChild;
	Integer key;

	public Node(Node leftChild, Node rightChild, Integer key) {
		this.leftChild = leftChild;
		this.rightChild = rightChild;
		this.key = key;
	}

	public Node(Integer key) {
		this.leftChild = null;
		;
		this.rightChild = null;
		this.key = key;
	}

	public Node() {
		this.leftChild = null;
		;
		this.rightChild = null;
		this.key = null;
	}

	public Node getLeftChild() {
		return leftChild;
	}

	public void setLeftChild(Node leftChild) {
		this.leftChild = leftChild;
	}

	public Node getRightChild() {
		return rightChild;
	}

	public void setRightChild(Node rightChild) {
		this.rightChild = rightChild;
	}

	public Integer getKey() {
		return key;
	}

	public void setKey(Integer key) {
		this.key = key;
	}

}
