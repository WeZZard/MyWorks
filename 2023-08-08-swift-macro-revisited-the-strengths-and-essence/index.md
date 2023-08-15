---
title: "Swift Macro: Revisited - The Strengths and Essence"
category: Programming
tags: [Swift, Macro]
isPublished: false
---

From the sessions at WWDC 2023, we learned that Swift Macro aims to:

- Eliminate boilerplates
- Make tedious things easy
- Share with other developers in packages

However, these goals aren't unique to Swift Macro. They are common
objectives for many language features in Swift, such as functions, types,
and modules. One could argue that all high-level programming languages
aspire to these ends. There must be something else that Swift Macro excels
at; otherwise, it would be redundant.

So, what is it that Swift Macro does exceptionally well?

Understanding the unique strengths of Swift Macro is crucial. It will
guide us in crafting Swift macros that are effective, inform us of the
boundaries when creating them, and ultimately lead us to produce
well-designed Swift macros. This understanding is the essence of Swift
Macro.

To grasp this, we need to first recognize the challenges that existing
Swift language features, like functions, types, and modules, have
addressed and their limitations. The key to understanding what set Swift
Macro apart lies in this exploration.

## What Existing Code Reuse Methods Managed To Solve?

### Functions

"Function" is ubiquitous in high-level programming languages. While they
might be called subroutines, routines, subprograms, or procedures in
different languages, their core purpose remains consistent: providing
reusable units of execution. This concept has remained consistent since
FORTRAN introduced it to high-level programming languages under the name
"subroutine".

The following example shows how to implement a function that sets the
value of `RESULT` based on whether `A` is positive, negative, or zero.

```FORTRAN
    SUBROUTINE CHECKNUM(A, RESULT)
    IF (A - 0) 10, 20, 30
10  RESULT = 0
    RETURN
20  RESULT = -1
    RETURN
30  RESULT = 1
    RETURN
    END
```

However, the FORTRAN "function," also known as a subroutine, had
significant areas for improvement. As programming evolved, programmers
then found that code could be better understood if:

- Variables are only accessible within the block of a control structure
  like the `IF` statement or loop.
- Control structures could be more expressive like using
  `IF-THEN-ELSE-END` instead of a simple `IF` statement.
- The `GOTO` statement could be eliminated by more advanced control
  structures.
- The "function" could be defined within other "functions".

All the aforementioned points contribute to the concept of structured
programming, a pivotal movement in computer science. ALGOL 60, a pioneer
in this movement, adopted these principles at a very early stage. Here is
an example that shows how expressive the control structure could
comparatively be in ALGOL 60.

```ALGOL
begin
  real procedure checknum(a);
    real a;
  begin
    if a < 0 then
      checknum := -1
    else if a = 0 then
      checknum := 0
    else
      checknum := 1
  end checknum;
end
```

Swift also adopted these principles, making them the foundational pillars
of its functions.

### Types

The adoption of structured programming enhanced program clarity,
encouraging more developers to enter the field. As software development
evolved to tackle more complex problems, the traditional methods of
organizing code — primarily through functions, files, and directories —
became limiting. While functions allowed for a granular level of logic
encapsulation, and files/directories provided a means to group related
code, there was a growing need for more sophisticated mechanisms to manage
and reuse code at different levels of granularity.

Simula, encoded designing for simulating real-world processes in its name,
introduced the concept of object-oriented programming, allowing developers
to create types with variables and functions as members. These members
were accessed via dot notations and were scoped within the type.
Additionally, one type could inherit from another, further enhancing code
reusability.

```Simula
BEGIN
  CLASS Animal;
  BEGIN
    Virtual: PROCEDURE Speak;
      BEGIN
        OutText("Some generic animal sound");
        OutImage;
      END Speak;
  END Animal;

  Animal CLASS Dog;
  BEGIN
    Virtual: PROCEDURE Speak;
    BEGIN
      OutText("Woof!");
      OutImage;
    END Speak;
  END Dog;

  Animal CLASS Cat;
  BEGIN
    Virtual: PROCEDURE Speak;
    BEGIN
      OutText("Meow!");
      OutImage;
    END Speak;
  END Cat;

  Dog myDog;
  Cat myCat;

  myDog.Speak;  ! This will output "Woof!"
  myCat.Speak;  ! This will output "Meow!"
END
```

These practices were then popularized by Smalltalk and later C++ and are
currently upheld by Swift types.

### Modules

However, programmers still faced challenges. How do you reuse code between
projects? By copying and pasting? And how do you speed up compilation when
frequently reusing code? By purchasing more powerful machines? Modula-2
introduced the concept of modules to address these issues, keeping
developers away from tedious pushes on keyboards and money talks.

Modules introduced by Modula-2 enabled the encapsulation of code at a
granularity greater than that of types, being more convenient than files
and directories. The following example shows how to import the `IO` module
and print the "Hello, world!" in Modula-2.

```Modula-2
MODULE Main;

IMPORT IO;

BEGIN
    IO.WriteString("Hello, world!");
    IO.WriteLn;
END Main.
```

More than that, the module that came with Modula-2 also brought separate
compilation and segregation between interfaces and implementations which
bring faster build speed and better software design. These advantages now
emerged in Swift modules.

By examining the evolution of code reuse, we can find that people tend to
create concepts that aggregate the smaller ones using a protective
mechanism. Here is the summary:

- Functions aggregate execution flows and variables and protect them
  with control structures and lexical scopes;
- Types aggregate variables and functions and protect them with
  instance name or type name;
- Modules aggregate variables, types and functions and protect them
  with the module's namespaces;

TODO: Figure: protection hierarchy of modules/types/functions

All these properties help us keep the code easy to understand as the code
size increases. These code reuse methods also built the existing hierarchy
of encapsulation in Swift.

However, what gives them advantages also caps their capabilities. Due to
the protective mechanisms over the encapsulation hierarchy, there are
still programming concepts that cannot be encapsulated -- because some
concepts are requiring us to drop this protection. Plus, none of these
code reuse methods can receive the programmer's source code as input --
they can only receive data or closures.

Now, we no longer can expand the types of encapsulate-able programming
concepts by merely following the established trends of existing code reuse
methods.

## What Swift Macros Do Exceptionally Well?

On the other hand, Swift Macro enables encapsulation over many of them by
embracing different design philosophies. To help you build a comprehensive
understanding of these design philosophies, I would like to show you the
nature of Swift Macro with some typical examples.

### Compile-Time Checked Literals

Design software like Figma and Sketch represent the RGB color with 6
hexadecimal digits. Developers often extend the type of color to allow
direct copying and pasting of RGB values from design software for use in
Swift:

```swift
import SwiftUI

// Color extension
extension Color {

  public init(_ hex: UInt)

}

// Use example
Color(0xFFEEAA)
```

But how do we verify that the pasted value is a valid RGB color? The
copy-and-paste operation does not ensure the correctness of the result.
The following code snippet shows a potential mistake that results in
copy-and-paste.

```swift
// Invalid color.
Color(0xFFEEA)
```

However, because Swift macros syntactically transform their arguments to
generate new code, we can integrate syntax checking during this
transformation. This allows for compile-time verification of 6-digit
hexadecimal RGB color "literals".

```swift
#Color(0xFFEEAA) // Compiled
// #Color expansion began
SwiftUI.Color(red: 1, green: 0.93, blue: 0.67)
// #Color expansion ended

#Color(0xFFEEA) // Invalid RGB, not compiled
```

TODO: Add a snapshot showing the Xcode reporting uncompiled code

From this example, you may be inspired to see how this compile-time safety
can be applied to other types of "literals".

### Code Style

In practice, we typically aim to avoid forcefully unwrapping optional
values using an exclamation mark:

```swift
func foo(_ bar: Int?) {
  print(bar!)
}
```

Instead, they prefer a safer approach using `guard let ... else`:

```swift
func foo(_ bar: Int?) {
  guard let bar else {
    return
  }
  print(bar)
}
```

However, this can be cumbersome, especially with multiple optional
parameters.

Given a programmer's inclination, there must be a desire to encapsulate
this unwrapping process for reuse. Unfortunately, since a function
protects its internal execution flow from inner functions' return for the
sake of structured programming, we cannot encapsulate this `guard let ...
else` in a function -- because the `return` statement in a function cannot
make the caller site function exit.

```swift
func guard<T>(_ value: T?) -> T {
  guard let value else {
    // This return cannot help `foo` to exit.
    // More than that, this function does not compile.
    return
  }
  return value
}

func foo(_ bar: Int?) {
  let bar = guard(bar)
  print(bar)
}
```

However, Swift Macro provides a feasible method for this type of
encapsulation. We can have a macro called `#unwrapped` which has the
following use example:

```swift
func foo(_ bar: Int?) {
  #unwrapped(bar) {
    print(bar)
  }
}
```

This could be expanded as:

```swift
func foo(_ bar: Int?) {
  // #unwrapped expansion began
  guard let bar = bar else {
    return
  }
  print(bar)
  // #unwrapped expansion ended
}
```

In the example above, the arguments of the `#unwrapped` macro: `bar` and
the trailing closure, undergo type-checking before the compiler initiates
the macro expansion process. This means the `bar` received by `print` in
the trailing closure would be bound to the parameter `_ bar: Int?` of the
`foo` function after the type-check.

However, once the macro expanded, since the expansion process itself could
be seen as a syntax replacement akin to copy-and-paste, the `bar` used by
`print` now is bound to the one declared by the `guard let bar` statement,
being unrelated to the type-check result before the macro expansion. More
than that, the `return` statement brought by this macro expansion now can
also affect the control flow of the applied site.

This example shows the evidence that the expansion of a freestanding Swift
macro could involve **control flow manipulation** and
**lexical scope sharing**.

### Extending Type's Behavior

The capabilities of Swift Macro are not bound to these boundaries. Let's
consider another kind of Swift Macro: attached macros and showcase its
potential with a real-life example.

In real-world scenarios, we often start from simple structs:

```swift
struct User {

  var name: String

  var avatar: URL

}
```

However, as the repository grows, the struct might expand proportionally:

```swift
struct User {

  var name: String

  var avatar: URL

  var avatarsInDifferentScales: [Int : URL]

  var userID: String

  var socialMedias: [String]

  var brief: String

  // ...

}
```

Since each property in the aforementioned struct requires heap allocation
for data storage, the cost of copying this struct also rises. The number
of heap allocations corresponds to the number of retaining operations
during the copy. Since retaining shall be guaranteed to be atomic, this
could potentially cause lagging in user interactions and waste in memory
space.

To minimize the struct's copying cost, we can aggregate the properties
into a class instance that acts as storage. This approach implements the
copy-on-write behavior in the original struct when altering the storage
contents:

```swift
struct User {

  // The heap storage type that aggregates the original stored properties
  // in the struct.
  private class Storage {

    var name: String

    // other properties ...

  }

  // The instance of the heap storage.
  private var _storage: Storage

  init(name: String, ...) {
    self._storage = Storage(name: name, ...)
  }

  // Offers copy-on-write behavior.
  private func makeStorageUniqueIfNeeded() {
    if !isKnownUniquelyReferenced(&_storage) {
      _storage = Storage(name: name, ...)
    }
  }

  // A rewritten property in the struct.
  var name: String {
    get { return _storage.name }
    set {
      makeStorageUniqueIfNeeded()
      _storage.name = newValue
    }
  }

  // Other rewritten properties ...

}
```

We can also illustrate the difference between the working details before
and after adopting the copy-on-write behavior:

TODO: An illustration that compares the working details before and after adopting the copy-on-write behavior.

In real-world testing, I improved the user experience of an app produced
by ByteDance by adopting this technique, increasing the FPS of a
particular scene from 48 to 56 and reducing the debug-time overall memory
usage by 600MB.

TODO: Before-after comparison for the optimization of the app I mentioned

But, again, this approach can be cumbersome. It not only involves a lot of
hand-roll code but, worse still, it increases the cost of maintaining the
program. With Swift Macro, we can do this more elegantly.

```swift
@COW
struct User {

  var name: String

  var avatar: URL

  var avatarsInDifferentScales: [Int : URL]

  var userID: String

  var socialMedias: [String]

  var brief: String

  // ...

}
```

Yes. Just as simple as I've shown. By adding an attached macro called
`@COW` to the struct, we have introduced the copy-on-write behavior to
this struct.

What this macro did is nothing more than what we have hand-rolled in the
previous code -- adding heap storage to the struct and transforming the
stored properties into computed properties that forward access to the heap
storage:

```swift
@COW
struct User {

  // @COW expansion began
  private class Storage {

    var name: String

    // other properties ...

  }

  private var _$storage: Storage

  private func makeStorageUniqueIfNeeded() {
    if !isKnownUniquelyReferenced(&_$storage) {
      _$storage = Storage(name: name, ...)
    }
  }

  init(name: String, ...) {
    self._$storage = Storage(name: name, ...)
  }
  // @COW expansion ended

  // @COW expansion began
  @COWIncluded(storage: _$storage)
  // @COW expansion ended
  var name: String {
    // @COWIncluded expansion began
    get { return _$storage.name }
    set {
      makeStorageUniqueIfNeeded()
      _$storage.name = newValue
    }
    // @COWIncluded expansion ended
  }

}
```

However, all these above happen in an automatic process that the Swift
compiler type-checks the `User` struct and then invokes the macro
expansion by using the type-checked `User` struct as an argument. Finally,
the `@COW` macro generates code by understanding the contents in the
`User` struct. With this automatic mechanism, the cost of maintenance has
not increased this time.

From the macro expansion shown above, it can be observed that attached
Swift macros can extend types with members and rewrite properties by
adding accessors. The extended contents not only bring new behaviors to
the type but also share the "namespace" of the extended point. It is also
worth noting that adding accessors to a stored property also changed its
semantics from a stored property into a computed property.

## Conclusion

By studying the historical context of code reuse methods in Swift and
understanding the characteristics of the newer Swift macros, we can draw
the following conclusions:

- Swift Macro is yet another form of encapsulation. It does not bring any
  new runtime capabilities.
- Swift Macro generates codes by transforming the programmer's code at
  the compile time. This means that we can also integrate other
  computations like compile-time checking into it.
- Unlike existing code reuse features in Swift, Swift Macro does not
  protect its expansion from the existing contents of the applied site by
  default. Yet, it also can change the semantics of the applied site.
  Macro authors shall watch out for potential traps and pitfalls while
  implementing Swift macros. To be specific:
  - For freestanding Swift macros, they can affect the control flow of the
    applied site as well as share the lexical scope.
  - For attached Swift macros, they can extend members to types as well as
    accessors to properties. The extended contents also share the same
    "namespace" of the extended point. More than that, accessor macros
    could turn a stored property into a computed property by adding either
    the `get`, `set` or whatever accessor.

TODO: Figure: modules/types/functions v.s. macro

These properties offer programmers not only another option for code reuse
but also the ability to encapsulate programming concepts that involve
compile-time checking, control flow manipulations, and adding behaviors to
types without relying on inheritance or other runtime techniques. These
properties have never been implemented in Swift before. Without a doubt,
they are the unique strengths that defined Swift Macro.

However, the same features that give Swift Macro its advantages also
introduce potential traps and pitfalls. We will delve into this topic in
the following post.

## Resources

- A playground project that implements the `#Color` and `#unwrapped`
  macro:

TODO: URL

- The production level implementation of the `@COW` macro:

TODO: URL
