/*
 * Simple Prime number checker
 * Usage:
 *  - java PrimeNumber 17
 *  - or run without args and enter a number when prompted
 */
import java.util.Scanner;

public class PrimeNumber {
    public static boolean isPrime(long n) {
        if (n <= 1) return false;
        if (n == 2) return true;
        if (n % 2 == 0) return false;
        long r = (long) Math.sqrt(n);
        for (long i = 3; i <= r; i += 2) {
            if (n % i == 0) return false;
        }
        return true;
    }

    public static void main(String[] args) {
        long n;
        if (args.length > 0) {
            try {
                n = Long.parseLong(args[0]);
            } catch (NumberFormatException e) {
                System.err.println("Invalid number: " + args[0]);
                System.exit(2);
                return;
            }
        } else {
            Scanner sc = new Scanner(System.in);
            System.out.print("Enter an integer to check for primality: ");
            if (!sc.hasNextLong()) {
                System.err.println("No integer provided.");
                sc.close();
                System.exit(2);
                return;
            }
            n = sc.nextLong();
            sc.close();
        }

        boolean prime = isPrime(n);
        System.out.println(n + (prime ? " is prime." : " is not prime."));
    }
}
