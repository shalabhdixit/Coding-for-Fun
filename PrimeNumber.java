public class PrimeNumber {
    /**
     * Return true if n is prime.
     */
    public static boolean isPrime(int n) {
        if (n <= 1) return false;
        if (n <= 3) return true;
        if (n % 2 == 0) return n == 2;
        int r = (int) Math.sqrt(n);
        for (int i = 3; i <= r; i += 2) {
            if (n % i == 0) return false;
        }
        return true;
    }

    /**
     * Print all primes from 2 up to max (inclusive).
     */
    public static void printPrimesUpTo(int max) {
        for (int i = 2; i <= max; i++) {
            if (isPrime(i)) System.out.println(i);
        }
    }

    public static void main(String[] args) {
        if (args.length == 0) {
            System.out.println("Usage: java PrimeNumber <number>\n       java PrimeNumber upTo <max>");
            System.out.println("Demo: primes up to 100:");
            printPrimesUpTo(100);
            return;
        }

        if (args.length == 2 && args[0].equalsIgnoreCase("upTo")) {
            try {
                int max = Integer.parseInt(args[1]);
                printPrimesUpTo(max);
            } catch (NumberFormatException e) {
                System.err.println("Invalid number: " + args[1]);
            }
            return;
        }

        try {
            int n = Integer.parseInt(args[0]);
            System.out.println(n + (isPrime(n) ? " is prime" : " is not prime"));
        } catch (NumberFormatException e) {
            System.err.println("Invalid number: " + args[0]);
        }
    }
}
