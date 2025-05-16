// Topic 8: Advanced TypeScript Features
// ---------------------------------------

// TypeScript offers a rich set of advanced features that allow developers to write
// more expressive, maintainable, and type-safe code. This section will explore
// some of these powerful capabilities.

console.log("Topic 8: Advanced TypeScript Features - File Created");

// 1. Generics
//   - Creating reusable, type-safe components (functions, classes, interfaces).
//   - Generic Constraints.
//   - Using Type Parameters in Generic Constraints.
//   - Using Class Types in Generics.
// Will be covered with examples below.

// 2. Decorators (Conceptual Overview)
//   - Metaprogramming for classes and their members (methods, properties, accessors, parameters).
//   - Class Decorators, Method Decorators, Property Decorators, Parameter Decorators.
//   - Decorator Factories.
//   - Composition of Decorators.
//   - Note: Decorators are an experimental feature in TypeScript and require enabling
//     `experimentalDecorators` and `emitDecoratorMetadata` in `tsconfig.json`.
//     Their usage is widespread in frameworks like Angular and NestJS.
// Will be covered with a conceptual explanation and a simple example if feasible without a framework context.

// 3. Advanced Types
//   - Conditional Types: Types that select one of two possible types based on a condition.
//   - Mapped Types: Creating new types by transforming properties of an existing type.
//   - Template Literal Types: Creating string literal types with template-like syntax.
//   - Utility Types: Built-in types that facilitate common type transformations.
//     - `Partial<Type>`: Constructs a type with all properties of Type set to optional.
//     - `Readonly<Type>`: Constructs a type with all properties of Type set to readonly.
//     - `Pick<Type, Keys>`: Constructs a type by picking the set of properties Keys from Type.
//     - `Omit<Type, Keys>`: Constructs a type by picking all properties from Type and then removing Keys.
//     - `Required<Type>`: Constructs a type with all properties of Type set to required.
//     - `Record<Keys, Type>`: Constructs an object type whose property keys are Keys and whose property values are Type.
//     - `Exclude<UnionType, ExcludedMembers>`: Excludes from UnionType all union members that are assignable to ExcludedMembers.
//     - `Extract<Type, Union>`: Extracts from Type all union members that are assignable to Union.
//     - `NonNullable<Type>`: Excludes null and undefined from Type.
//     - `ReturnType<Type>`: Obtains the return type of a function type.
//     - `InstanceType<Type>`: Obtains the instance type of a constructor function type.
// Will be covered with examples for each.

// 4. Type Guards and Narrowing
//   - `typeof` type guards.
//   - `instanceof` type guards.
//   - `in` operator type guard.
//   - Equality narrowing (e.g., `===`, `!==`).
//   - Truthiness narrowing.
//   - User-Defined Type Guards (using `is` keyword).
//   - Discriminated Unions (Tagged Unions).
// Will be covered with examples.

// 5. Using `interface` vs. `type` Effectively
//   - Key differences: Declaration merging (interfaces), implementing/extending (interfaces), primitive types/unions/tuples (types).
//   - When to use which: General guidelines and common patterns.
// Will be discussed with illustrative examples.

// Let's start by diving into Generics.
console.log("\n--- 1. Generics ---");

// Generics enable writing components that work with a variety of types rather than a single one,
// while preserving type safety. They use type parameters, typically denoted by `T`, `U`, `K`, `V`, etc.

// 1.1. Generic Functions
// ======================

// With generics first:
function identity<T>(arg: T): T {
    return arg;
}
const outputString = identity<string>("myString");
const outputNumber = identity(100);

// A simple identity function that returns whatever is passed to it.
// Without generics, you might use `any`, losing type information.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function identityAny(arg: any): any {
    return arg;
}
// eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars
const outputAny = identityAny("myString"); // outputAny is of type any

console.log(`Generic identity<string>("myString"): ${outputString}`);
console.log(`Generic identity(100): ${outputNumber}`);

// Working with arrays
function getFirstElement<T>(arr: T[]): T | undefined {
    return arr.length > 0 ? arr[0] : undefined;
}
const numArray = [1, 2, 3];
const strArray = ["a", "b", "c"];
console.log(`First element of [1,2,3]: ${getFirstElement(numArray)}`);
console.log(`First element of ["a","b","c"]: ${getFirstElement(strArray)}`);
console.log(`First element of []: ${getFirstElement([])}`);

// 1.2. Generic Interfaces
// =======================
interface GenericPair<K, V> {
    key: K;
    value: V;
}

const pair1: GenericPair<string, number> = { key: "age", value: 30 };
const pair2: GenericPair<number, boolean> = { key: 123, value: true };
console.log("GenericPair<string, number>: ", pair1);
console.log("GenericPair<number, boolean>: ", pair2);

// 1.3. Generic Classes
// ====================
class GenericContainer<T> {
    private contents: T;

    constructor(initialContents: T) {
        this.contents = initialContents;
    }

    getContents(): T {
        return this.contents;
    }

    setContents(newContents: T): void {
        this.contents = newContents;
    }
}

const stringContainer = new GenericContainer<string>("Hello Generics!");
console.log(`stringContainer.getContents(): ${stringContainer.getContents()}`);
stringContainer.setContents("TypeScript is cool.");
console.log(`stringContainer.getContents() after set: ${stringContainer.getContents()}`);

const numberContainer = new GenericContainer(42); // Type inference
console.log(`numberContainer.getContents(): ${numberContainer.getContents()}`);

// 1.4. Generic Constraints
// ========================
// Sometimes you want to limit the types that can be used with a generic type parameter.
// For example, you might want a function that operates on types that have a `length` property.

interface Lengthwise {
    length: number;
}

function logLength<T extends Lengthwise>(arg: T): void {
    console.log(`Length of argument: ${arg.length}`);
}

logLength("hello"); // string has a length property
logLength([1, 2, 3]); // array has a length property
// logLength(10); // Error: number does not have a length property
logLength({ length: 10, value: 3 }); // Works, as it satisfies the Lengthwise interface

// 1.5. Using Type Parameters in Generic Constraints
// ===============================================
// You can declare a type parameter that is constrained by another type parameter.
// For example, getting a property from an object given the object and the key's name.
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
    return obj[key];
}

const car = { make: "Toyota", model: "Camry", year: 2022 };
const carMake = getProperty(car, "make");
const carModel = getProperty(car, "model");
// const carColor = getProperty(car, "color"); // Error: "color" is not a key of car
console.log(`getProperty(car, "make"): ${carMake}`);
console.log(`getProperty(car, "model"): ${carModel}`);

// 1.6. Using Class Types in Generics
// ==================================
// When creating factories using generics, it can be useful to refer to class types by their constructor functions.
function createInstance<T>(constructorFunc: { new (): T; }): T {
    return new constructorFunc();
}

class Greeter {
    greeting: string;
    constructor() {
        this.greeting = "Hello, from Greeter!";
    }
    greet() {
        console.log(this.greeting);
    }
}

class Dog {
    name: string;
    constructor() {
        this.name = "Buddy";
    }
    bark() {
        console.log(`Woof! My name is ${this.name}`);
    }
}

const greeterInstance = createInstance(Greeter);
greeterInstance.greet();

const dogInstance = createInstance(Dog);
dogInstance.bark();

// Next, we'll look at Decorators.
console.log("\n--- 2. Decorators (Conceptual Overview) ---");

// Decorators are a special kind of declaration that can be attached to a class declaration,
// method, accessor, property, or parameter. Decorators use the form `@expression`,
// where `expression` must evaluate to a function that will be called at runtime
// with information about the decorated declaration.

// Key points about Decorators:
// - They provide a way to add annotations and a meta-programming syntax for class declarations and members.
// - They are a Stage 3 ECMAScript proposal (as of late 2023/early 2024, check current status) and are available in TypeScript as an experimental feature.
// - To use decorators, you must enable the `experimentalDecorators` compiler option in your `tsconfig.json` file.
//   You might also need `emitDecoratorMetadata` if you are working with reflection (often used with IoC containers).
//   Example `tsconfig.json` settings:
//   {
//     "compilerOptions": {
//       "target": "ES6",
//       "experimentalDecorators": true,
//       "emitDecoratorMetadata": true
//     }
//   }

// Types of Decorators:
// 1. Class Decorators: Applied to the constructor of a class. Used to observe, modify, or replace a class definition.
//    - Receives the constructor of the class as its single argument.
// 2. Method Decorators: Applied to a method on a class.
//    - Receives three arguments: the target (static member: class constructor; instance member: prototype), the member name, and a property descriptor.
// 3. Accessor Decorators: Similar to method decorators, but for accessors (get/set).
//    - Receives the same three arguments as method decorators.
// 4. Property Decorators: Applied to a property of a class.
//    - Receives two arguments: the target and the member name.
// 5. Parameter Decorators: Applied to a parameter of a method or constructor.
//    - Receives three arguments: the target, the member name (of the method/constructor), and the ordinal index of the parameter.

// Decorator Factories
// - If you want to customize how a decorator is applied to a declaration, you can write a decorator factory.
// - A decorator factory is simply a function that returns the function that will be called by the decorator at runtime.

// Decorator Composition
// - Multiple decorators can be applied to a single declaration.
// - They are evaluated bottom-up (the result of the lower decorator is passed to the higher one).

// Simple Class Decorator Example (Conceptual)
// Note: To run this, `experimentalDecorators` must be enabled in tsconfig.

// Using Function type for simplicity in this conceptual example, though linters might prefer more specific types.
// eslint-disable-next-line @typescript-eslint/ban-types
function sealed(constructorFn: Function) {
    Object.seal(constructorFn);
    Object.seal(constructorFn.prototype);
    console.log(`LOG: Class ${constructorFn.name} has been sealed.`);
}

@sealed
class BugReport {
    type = "report";
    title: string;

    constructor(t: string) {
        this.title = t;
    }
}

const bug = new BugReport("Button not working");
console.log(bug);
// Attempting to add a new property to a sealed class or its prototype will fail silently or throw in strict mode.
// (bug as any).newProperty = 123; // This would typically not work as expected.
// BugReport.prototype.newMethod = () => {}; // This would also not work.

console.log("Decorators are powerful but use them judiciously, understanding their experimental nature and impact.");
console.log("They are most commonly seen in frameworks like Angular and NestJS for DI, ORM, etc.");

// Next, we will cover Advanced Types. 