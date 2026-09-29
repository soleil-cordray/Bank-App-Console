/*
* BankApp: Single Flow Console Application
* Main -> Welcome Message -> Authentication/Authorization(Login)
* 2 stakeholders: Admin, Customer
* 2 dashboard/menus: AdminMenu, CustomerMenu
* Operations: CRUD( Add Customer,Delete,Update, Add Account, View All Accounts)
* Programming and OOD concepts
* Loops and single flow
* */

import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;


public class Main {

    static Scanner sc = new Scanner(System.in);
    //If user is admin, username is "admin", password is "admin123"
    //If user is customer, below registrations are valid
    static int counter = 1;
    static List<Customer> customers = new ArrayList<Customer>();
    static List<User> users = new ArrayList<>();

    static{
        User u1 = new User("rohit","rohit123");
        User u2 = new User("mohit","mohit123");
        User u3 = new User("shobhit","shobhit123");
        users.add(u1);users.add(u2);users.add(u3);

        Customer c1 = new Customer(counter++, "rohit", new ArrayList<>(),u1.username,u1.password);
        Customer c2 = new Customer(counter++, "mohit", new ArrayList<>(),u2.username,u2.password);
        Customer c3 = new Customer(counter++, "shohit", new ArrayList<>(),u3.username,u3.password);
        customers.add(c1);  customers.add(c2);  customers.add(c3);


    }


    public static void main(String[] args) {
       welcome();
       String loginResult = login();

       if(loginResult.equals("validation_failed")){
           System.out.println("Validation Failed");
       }

       if(loginResult.equals("admin")){
           adminDashboard();
       }
       else{
           customerDashboard(loginResult);
       }
    }

    private static void customerDashboard(String loginResult) {
        System.out.println("Welcome customer, " + loginResult);
        //switch case to present options: See his account, read account-balance
    }

    private static void adminDashboard() {
        System.out.println("Welcome Admin");
        //switch case to present option: See all customer, see all accounts, delete any account
    }


    private static String login() {
        System.out.println("Please enter username and password, space separated");
        String enteredUsernamePassword = sc.nextLine();
        //validation can be done
        //rohit rohit123

        String[] usernamePassword = enteredUsernamePassword.split(" ");
        String username = usernamePassword[0];//rohit
        String password = usernamePassword[1];//rohit123

        if(username.equals("admin") && password.equals("admin123")){
            return "admin";
        }

        //customer login
        for(User user:users){
            if(user.username.equals(username) && user.password.equals(password)){
                return user.username;
            }
        }

        return "validation_failed";
    }

    private static void welcome() {
        System.out.println("Welcome to ABC Digital Bank");
    }
}

class User{
    String username;
    String password;

    public User(String username, String password) {
        this.username = username;
        this.password = password;
    }
}


class Customer extends User{
    private int id;
    private String name;
    private List<Account> accounts;
    private String username;
    private String password;

    public Customer(int id, String name, List<Account> accounts, String username, String password) {
        super(username,password);
        this.id = id;
        this.name = name;
        this.accounts = accounts;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public List<Account> getAccounts() {
        return accounts;
    }

    public void setAccounts(List<Account> accounts) {
        this.accounts = accounts;
    }

    public String toString() {
        return "Customer{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", accounts=" + accounts +
                '}';
    }
}

class Admin extends User{
  int id;
  String username = "admin";
  String password = "admin123";

    public Admin(String username, String password) {
        super(username, password);
    }
}

abstract class Account{
    int id;
    int balance;
    abstract double addInterest();
}

class CheckinsAccount extends Account{
    String accountType = "ChekingsAccount";

    double addInterest() {
        //add 2% to current balance and return updated balance;
        return 0.0;
    }
}

class SavingsAccount extends Account{
    String accountType = "SavingsAccount";

    double addInterest() {
        //add 3% to current balance and return updated balance;
        return 0.0;
    }
}