package workshop.track1;

import java.util.*;

public class InventoryAPI {
    private final Map<String, Map<String, Object>> products = new HashMap<>();

    /**
     * Lists products with pagination support.
     *
     * <p>Returns a paginated slice of the product catalog. Pages are 1-indexed.
     * If the requested page exceeds available data, an empty items list is returned.
     * Results are unordered since the backing store is a HashMap.
     *
     * <p><b>Pagination notes:</b> The {@code page} parameter is 1-based. A {@code pageSize}
     * of 0 returns an empty slice. Out-of-range pages return empty items with correct totals.
     *
     * @param page     the 1-based page number to retrieve
     * @param pageSize the maximum number of items per page
     * @return a map containing:
     *         <ul>
     *           <li>{@code "items"} — {@code List<Map<String, Object>>} the product slice</li>
     *           <li>{@code "page"} — {@code int} the requested page number</li>
     *           <li>{@code "page_size"} — {@code int} the requested page size</li>
     *           <li>{@code "total"} — {@code int} total number of products</li>
     *         </ul>
     *
     * <pre>{@code
     * // Example:
     * Map<String, Object> result = api.listProducts(1, 10);
     * List<?> items = (List<?>) result.get("items");
     * int total = (int) result.get("total");
     * }</pre>
     */
    public Map<String, Object> listProducts(int page, int pageSize) {
        List<Map<String, Object>> items = new ArrayList<>(products.values());
        int start = Math.max(0, (page - 1) * pageSize);
        int end = Math.min(items.size(), start + pageSize);
        List<Map<String, Object>> slice = items.subList(start, end);
        Map<String, Object> result = new HashMap<>();
        result.put("items", slice);
        result.put("page", page);
        result.put("page_size", pageSize);
        result.put("total", items.size());
        return result;
    }

    /**
     * Retrieves a single product by its unique identifier.
     *
     * @param productId the UUID of the product to retrieve
     * @return a map containing the product fields: {@code id}, {@code name},
     *         {@code price}, {@code tags}, and {@code in_stock}
     * @throws NoSuchElementException if no product exists with the given ID
     *
     * <pre>{@code
     * // Example:
     * Map<String, Object> product = api.getProduct("some-uuid");
     * String name = (String) product.get("name");
     * }</pre>
     */
    public Map<String, Object> getProduct(String productId) {
        Map<String, Object> product = products.get(productId);
        if (product == null) throw new NoSuchElementException("product not found");
        return product;
    }

    /**
     * Creates a new product in the inventory.
     *
     * <p>Generates a random UUID as the product identifier. Tags default to an
     * empty list if {@code null} is provided.
     *
     * @param name    the product display name
     * @param price   the product price; must be non-negative
     * @param tags    optional list of string tags; {@code null} is treated as empty
     * @param inStock whether the product is currently in stock
     * @return a map containing the created product with fields: {@code id},
     *         {@code name}, {@code price}, {@code tags}, and {@code in_stock}
     * @throws IllegalArgumentException if {@code price} is negative
     *
     * <pre>{@code
     * // Example:
     * Map<String, Object> product = api.createProduct(
     *     "Widget", 9.99, Arrays.asList("hardware", "sale"), true);
     * String id = (String) product.get("id");
     * }</pre>
     */
    public Map<String, Object> createProduct(String name, double price, List<String> tags, boolean inStock) {
        if (price < 0) throw new IllegalArgumentException("price must be non-negative");
        String id = UUID.randomUUID().toString();
        Map<String, Object> product = new HashMap<>();
        product.put("id", id);
        product.put("name", name);
        product.put("price", price);
        product.put("tags", tags != null ? tags : new ArrayList<>());
        product.put("in_stock", inStock);
        products.put(id, product);
        return product;
    }

    /**
     * Updates an existing product with the provided field values.
     *
     * <p>Merges the entries from {@code updates} into the existing product map,
     * overwriting any matching keys.
     *
     * @param productId the UUID of the product to update
     * @param updates   a map of field names to new values
     * @return the updated product map
     * @throws NoSuchElementException if no product exists with the given ID
     *
     * <pre>{@code
     * // Example:
     * api.updateProduct(id, Map.of("price", 8.99, "in_stock", false));
     * }</pre>
     */
    public Map<String, Object> updateProduct(String productId, Map<String, Object> updates) {
        Map<String, Object> product = products.get(productId);
        if (product == null) throw new NoSuchElementException("product not found");
        for (Map.Entry<String, Object> kv : updates.entrySet()) {
            product.put(kv.getKey(), kv.getValue());
        }
        return product;
    }

    /**
     * Deletes a product from the inventory.
     *
     * @param productId the UUID of the product to delete
     * @return a map containing {@code "id"} (the deleted product's ID) and
     *         {@code "deleted"} ({@code true})
     * @throws NoSuchElementException if no product exists with the given ID
     *
     * <pre>{@code
     * // Example:
     * Map<String, Object> result = api.deleteProduct("some-uuid");
     * boolean deleted = (boolean) result.get("deleted");
     * }</pre>
     */
    public Map<String, Object> deleteProduct(String productId) {
        Map<String, Object> removed = products.remove(productId);
        if (removed == null) throw new NoSuchElementException("product not found");
        Map<String, Object> meta = new HashMap<>();
        meta.put("id", productId);
        meta.put("deleted", true);
        return meta;
    }

    /**
     * Demonstrates basic CRUD operations on the inventory API.
     *
     * <p>Creates sample products, lists, retrieves, updates, and deletes them,
     * printing results to stdout.
     */
    public static void demo() {
        InventoryAPI api = new InventoryAPI();
        Map<String, Object> p1 = api.createProduct("Widget", 9.99, Arrays.asList("hardware", "sale"), true);
        Map<String, Object> p2 = api.createProduct("Gadget", 14.99, Collections.singletonList("hardware"), true);
        System.out.println("List size=" + ((List<?>) api.listProducts(1, 10).get("items")).size());
        System.out.println("Get name=" + api.getProduct((String) p1.get("id")).get("name"));
        api.updateProduct((String) p1.get("id"), Map.of("price", 8.99));
        System.out.println("Updated price=" + api.getProduct((String) p1.get("id")).get("price"));
        api.deleteProduct((String) p2.get("id"));
        System.out.println("Deleted second product.");
    }

    public static void main(String[] args) { demo(); }
}
